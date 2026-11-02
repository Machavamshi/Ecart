from flask import Flask, render_template, redirect, url_for, request, make_response,flash, jsonify

import jwt
from datetime import datetime, timedelta, timezone

from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Razorpay imports
import razorpay

# ------------import database logics -------------------
from database.tables import createTables
from database.utility import checkUserExists, addUser, getUserDetails, getCatagoriesFromDB, getProductsFromDB
from database.utility import addProductToDB, totalOrdersCount, getOrders, usersDetails, getUserDetailsByID, updateAdminProfile
from database.utility import getProductDetailsByID, updateProductInfo, updateProductStatus, viewUserByAdmin
from database.utility import addToCart, getCartItems, removeFromCart, updateCartQuantity, clearCart, getCartTotal
from database.user_utility import view_users_orders, show_category, user_profile_details, update_user_profile
from database.payment_utility import create_razorpay_order, create_order_in_db, clear_user_cart, get_cart_items_for_checkout, get_cart_total_amount, verify_payment

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'srinubabu@123')

# Razorpay API Keys - UPDATE WITH YOUR KEYS
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '').strip()
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '').strip()

# Debug: Check if keys are loaded
if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    print("WARNING: Razorpay API keys not configured!")
    print(f"RAZORPAY_KEY_ID: {'Set' if RAZORPAY_KEY_ID else 'NOT SET'}")
    print(f"RAZORPAY_KEY_SECRET: {'Set' if RAZORPAY_KEY_SECRET else 'NOT SET'}")
else:
    print(f"✓ Razorpay configured with Key ID: {RAZORPAY_KEY_ID[:20]}...")

# Upload folder configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads/profile')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



## -------------------------- Helper Functions ------------------------------------


## token protection decorator
def token_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.cookies.get('token')

            if not token:
                return redirect(url_for('login'))

            try:
                data = jwt.decode(
                    token,
                    app.config['SECRET_KEY'],
                    algorithms=["HS256"]
                )
            except jwt.ExpiredSignatureError:
                return redirect(url_for('login'))
            except jwt.InvalidTokenError:
                return redirect(url_for('login'))

            if role and data['role'] != role:
                return "Unauthorized access"

            return f(*args, **kwargs)
        return decorated
    return wrapper


def getUserByToken():
    token = request.cookies.get('token')

    if not token:
        return None

    try:
        data = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )

        userid = data.get('userid')
        role = data.get('role')

        user = getUserDetailsByID(userid=userid)

        return user

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


# login route
@app.route("/login", methods=['GET',"POST"])
def login():
    # if it is POST request method
    # get form data
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
       
        # user validation
        data = getUserDetails(email=username)
        print(data)
        if data and check_password_hash(data['password'], password):
            
            # create login token
            # utc_now = datetime.now(timezone.utc)

            # Add 2 hours
            exp_time = datetime.now(timezone.utc) + timedelta(hours=2)

            token = jwt.encode(
                {
                    "userid": data["userid"],
                    "role": data["role"],
                    "exp": exp_time
                },
                app.config['SECRET_KEY'],
                algorithm="HS256"
            )

             # Based on role it selects the user dashbord or admin dashboard
            response = make_response(
                redirect(url_for('admin' if data['role']=='admin' else 'user'))
            )

            # store token in cookie
            response.set_cookie(
                'token',
                token,
                httponly=True,
                secure=False  # True in production (HTTPS)
            )

            return response
        # If credintial is incorrect
        flash('User Credentials incorrect')
        return redirect(url_for('login'))

    # if it is get request 
    return render_template('auth/login.html')


#registe Route
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        profile_image = request.files.get('profile_image')

        # basic validation
        if not name or not email or not phone or not password:
            flash("All required fields must be filled")
            return redirect(url_for('register'))

        # check user already exists
        if checkUserExists(email=email):
            flash("Email already registered")
            return redirect(url_for('register'))

        # password hash
        hashed_password = generate_password_hash(password)

        # handle profile image
        image_path = None
        if profile_image and profile_image.filename != "":
            if allowed_file(profile_image.filename):
                filename = secure_filename(profile_image.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                image_path = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )

                profile_image.save(image_path)
            else:
                flash("Invalid image format")
                return redirect(url_for('register'))

        # add user to database
        addUser(
            name=name,
            email=email,
            phone_number=phone,
            password=hashed_password,
            profile_image=image_path
        )

        flash("Registration successful. Please login.")
        return redirect(url_for('login'))

    return render_template('auth/register.html')

# forgotpassword route
@app.route('/forgotpassword')
def forgotpassword():
    return "forgot Password Page"



## Admin Routes
# admin dashborad route
@app.route('/admin')
@token_required(role='admin')
def admin():

    total_products = 10 # need to update in utilituy
    total_orders = totalOrdersCount()
    pending_orders = 10 # need to update in utilituy
    total_users = 10 # need to update in utilituy
    return render_template('admin/dashboard.html',
                            total_products=total_products,
                            total_orders=total_orders,
                            pending_orders=pending_orders,
                            total_users=total_users
                        )

# product route

@app.route('/admin/products')
@token_required(role='admin')
def adminproducts():
    # get all categories name 
    categories = getCatagoriesFromDB()

    product_name = request.args.get('name',"")
    category = request.args.get('category', "")
    status = request.args.get('status', "")

    print(category, product_name, status)
    # Get all products from  database
    products = getProductsFromDB(name=product_name, category= category, status= status)
    # print(products[:3])
    return render_template('admin/products.html', categories= categories, products=products)

# Add product Route

@app.route('/admin/addproduct', methods = ['GET','POST'])
@token_required(role='admin')
def adminaddproduct():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        active = request.form['active']
        price = request.form['price']
        stock = request.form['stock']
        image = request.files.get('image')

        # handle product image (save to static/uploads and store relative path)
        image_url = None
        if image and image.filename != "":
            if allowed_file(image.filename):
                filename = secure_filename(image.filename)
                uploads_dir = os.path.join('static', 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                save_path = os.path.join(uploads_dir, filename)
                image.save(save_path)
                # store relative path used by url_for('static', filename=...)
                image_url = os.path.join('uploads', filename).replace('\\', '/')
            else:
                flash("Invalid image format")
                return redirect(url_for('adminaddproduct'))

        # add products details into products table (include image_url if present)
        addProductToDB(name=name,
                       description=description,
                       category=category,
                       price=price,
                       stock=stock,
                       active=active,
                       image_url=image_url)
        flash("Product added successfully","success")
        return redirect(url_for('adminproducts')) # after redirect to products page

    return render_template('admin/addproduct.html')


@app.route('/admin/editproduct/<int:productid>', methods=['GET', 'POST'])
@token_required(role='admin')
def editproduct(productid):
    # get product data from database
    product = getProductDetailsByID(productid=productid)
    # if request is post 
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        price = request.form.get('price')
        stock = request.form.get('stock')
        active = request.form.get('active')
        # update with new data in database
        if updateProductInfo(name, description,category, price, stock, active, productid):
            flash("Product updated successfully", "success")
            return redirect(url_for('adminproducts'))
        flash("Product NoT updated", "Error")
        return redirect(url_for('adminproducts'))

    return render_template('admin/edit_product.html',product = product)

# deactivate user
# view user 
@app.route('/admin/deactivate_product/<int:productid>', methods=['POST'])
@token_required(role='admin')
def deactivate_product(productid):
    # update in database
    status = updateProductStatus(productid=productid, status=0)
    if status:
        flash("Product deactivated successfully", "warning")
        return redirect(url_for('adminproducts'))
    flash("Product Not deactivated", "Error")
    return redirect(url_for('adminproducts'))
    
@app.route('/admin/activate_product/<int:productid>', methods=['POST'])
@token_required(role='admin')
def activate_product(productid):
    # update in database
    status = updateProductStatus(productid=productid, status=1)
    if status:
        flash("Product Activates successfully", "warning")
        return redirect(url_for('adminproducts'))
    flash("Product Not activated", "Error")
    return redirect(url_for('adminproducts'))
    

@app.route('/admin/users')
@token_required(role='admin')
def adminusers():

    # filters
    name = request.args.get('name', '').strip()
    email = request.args.get('email', '').strip()
    role = request.args.get('role', '').strip()
    users = usersDetails(name=name, email=email, role=role)
    

    return render_template(
        "admin/users.html",
        users=users,
        total_users=len(users)
    )


# orders Route

@app.route('/admin/orders')
@token_required(role='admin')
def adminorders():
    # get filter parameter 
    orderid = request.args.get('orderid',"")
    product_name = request.args.get('productname',"")
    from_date = request.args.get('fromdate',"")
    to_date = request.args.get('todate',"")

    orders_count = totalOrdersCount()
    # getting filterd orders
    orders = getOrders(orderid=orderid,
                       product_name=product_name,
                       from_date=from_date,
                       to_date=to_date)
    filter_orders_count = len(orders)
    # print(orders[:3])

    return render_template('admin/orders.html',
                            total_orders = orders_count,
                            filtred_order_count=filter_orders_count,
                            orders=orders)


# view user 
@app.route('/admin/viewuser/<int:userid>', methods=['GET', 'POST'])
@token_required(role='admin')
def view_user(userid):

    # get user data from database
    user = viewUserByAdmin(userid=userid)
    if not user:
        flash("User not found", "danger")
        return redirect(url_for('adminusers'))

    return render_template(
        'admin/view_user.html',
        user=user
    )
    

# deactivate user
# view user 
@app.route('/admin/deactivate/<int:userid>', methods=['GET', 'POST'])
@token_required(role='admin')
def deactivate_user(userid):
    return "deactivate user"


# view order details (minimal safe implementation)
@app.route('/admin/vieworder/<int:order_id>')
@token_required(role='admin')
def view_order(order_id):
    # reuse getOrders util to fetch the order by ORDER_ID
    orders = getOrders(orderid=order_id)
    order = orders[0] if orders else None
    return render_template('admin/view_order.html', order=order)


# admin profile route

@app.route('/admin/profile', methods=['GET', 'POST'])
@token_required(role='admin')
def adminprofile():

    user = getUserByToken()   # helper → decodes token, returns user data

    if request.method == 'POST':

        name = request.form.get('name')
        phone = request.form.get('phone')

        update_user_profile(
            userid=user.get('userid'),
            name=name,
            phone=phone
        )

        flash("Profile updated successfully", "success")
        return redirect(url_for('adminprofile'))

    return render_template(
        'admin/profile.html',
        user=user
    )



@app.route('/admin/change-password', methods=['POST'])
def admin_change_password():
    user = getUserByToken()

    if not user or user.get('role') != 'admin':
        return redirect(url_for('login'))

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    # Verify current password
    if not check_password_hash(user.get('password'), current_password):
        return redirect(url_for('admin_profile'))

    hashed_password = generate_password_hash(new_password)

    
    # update admin profile in database
    updateAdminProfile(new_password=hashed_password, userid=user.get('userid'))

    return redirect(url_for('admin_profile'))



@app.route('/admin/logout')
def adminlogout():
    response = make_response(redirect(url_for('login')))

    # delete token cookie
    response.set_cookie(
        'token',
        '',
        expires=0,
        httponly=True
    )

    return response


# --------------------------------User Routes --------------------------------#
#User dashboard route
@app.route('/user')
@token_required(role='user')
def user():
    search_term = request.args.get('search_product', '').strip()

    # fetch products (if search_term empty -> all products)
    products = getProductsFromDB(name=search_term)

    return render_template('user/user.html', products=products, search_query=search_term)
#home route
@app.route('/user/home')
@token_required(role='user')
def user_home():
    # search term from query params
    search_term = request.args.get('search_product', '').strip()

    # fetch products (if search_term empty -> all products)
    products = getProductsFromDB(name=search_term)

    return render_template('user/user.html', products=products, search_query=search_term)

#user category_____________________________-
@app.route('/user/categories')
@token_required(role='user')
def user_categories():

    category = request.args.get('category')
    items =[]

    if category:
        items = show_category(category)

    return render_template(
        'user/categories.html',
        items=items,
        selected_category=category
    )



#user orders______________________________________

@app.route('/users/orders')
@token_required(role='user')
def user_orders():

    user = getUserByToken()

    if not user:
        return redirect(url_for('login'))

    user_id =  user.get('userid')

    if not user_id:
        return "User ID not found in database result"

    orders = view_users_orders(user_id)

    return render_template("user/user_orders.html", orders=orders)



# cart route
@app.route('/user/cart', methods=['GET', 'POST'])
@token_required(role='user')
def user_cart():
    user = getUserByToken()
    
    if not user:
        return redirect(url_for('login'))
    
    user_id = user.get('userid')
    
    if not user_id:
        return "User ID not found in database result"
    
    # Handle POST request - Add item to cart
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity', 1)
        
        if product_id:
            try:
                quantity = int(quantity)
                if quantity > 0:
                    addToCart(user_id, int(product_id), quantity)
                    flash('Item added to cart successfully!', 'success')
            except (ValueError, TypeError):
                flash('Invalid quantity', 'error')
        
        return redirect(url_for('user_cart'))
    
    # Handle GET request - Display cart items
    cart_items = getCartItems(user_id)
    cart_total = getCartTotal(user_id)
    
    return render_template('user/cart.html', cart_items=cart_items, cart_total=cart_total)    
    

@app.route('/buy_now/<int:product_id>', methods=['POST'])
@token_required(role='user')
def buy_now(product_id):
    user = getUserByToken()
    
    if not user:
        return redirect(url_for('login'))
    
    user_id = user.get('userid')
    if not user_id:
        return "User ID not found in database result"

    try:
        addToCart(user_id, product_id, 1)
        flash('Item added to cart. Please proceed to checkout.', 'success')
    except Exception:
        flash('Unable to add item to cart.', 'error')

    return redirect(url_for('checkout'))


# Update cart item quantity
@app.route('/user/cart/update-quantity', methods=['POST'])
@token_required(role='user')
def update_cart_quantity():
    user = getUserByToken()
    
    if not user:
        return redirect(url_for('login'))
    
    user_id = user.get('userid')
    cart_id = request.form.get('cart_id')
    quantity = request.form.get('quantity')
    
    if cart_id and quantity:
        try:
            quantity = int(quantity)
            if quantity > 0:
                updateCartQuantity(int(cart_id), user_id, quantity)
                flash('Cart updated!', 'success')
            else:
                removeFromCart(int(cart_id), user_id)
                flash('Item removed from cart!', 'success')
        except (ValueError, TypeError):
            flash('Invalid quantity', 'error')
    
    return redirect(url_for('user_cart'))


# Remove item from cart
@app.route('/user/cart/remove', methods=['POST'])
@token_required(role='user')
def remove_from_cart():
    user = getUserByToken()
    
    if not user:
        return redirect(url_for('login'))
    
    user_id = user.get('userid')
    cart_id = request.form.get('cart_id')
    
    if cart_id:
        removeFromCart(int(cart_id), user_id)
        flash('Item removed from cart!', 'success')
    
    return redirect(url_for('user_cart'))    
    
    

# user profile route
# @app.route('/user/profile')
# @token_required(role='user')
# def user_profile():
    # user = getUserByToken()
    # if not user:
    #     return redirect(url_for('login'))

    # user_id =  user.get('USERID')

    # if not user_id:
    #     return "User ID not found in database result"
    
    # profile=user_profile_details(user_id)
    
    # return render_template("user/user_profile.html",profile=profile)

@app.route('/user/profile', methods=['GET', 'POST'])
@token_required(role='user')
def user_profile():
    user = getUserByToken()

    if not user:
        return redirect(url_for('login'))

    user_id = user.get('userid')

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        profile_image = request.files.get('profile_image')

        image_path = None
        if profile_image and profile_image.filename != "":
            if allowed_file(profile_image.filename):
                filename = secure_filename(profile_image.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_image.save(save_path)
                # store relative path for templates
                image_path = os.path.join('uploads', 'profile', filename).replace('\\', '/')
            else:
                flash("Invalid image format", "error")
                return redirect(url_for('user_profile'))

        # call DB helper to update user profile
        update_user_profile(userid=user_id, name=name, phone=phone, profile_image=image_path)
        flash("Profile updated successfully", "success")
        return redirect(url_for('user_profile'))

    # GET: fetch latest profile from DB and render user profile template
    profile = user_profile_details(user_id)
    return render_template('user/user_profile.html', profile=profile)



@app.route('/user/change-password', methods=['POST'])
def user_change_password():
    user = getUserByToken()

    if not user or user.get('role') != 'user':
        return redirect(url_for('login'))

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    # Verify current password
    if not check_password_hash(user.get('password'), current_password):
        return redirect(url_for('user_profile'))

    hashed_password = generate_password_hash(new_password)

    
    # update admin profile in database
    updateAdminProfile(new_password=hashed_password, userid=user.get('userid'))

    return redirect(url_for('admin_profile'))



@app.route('/user/logout')
def userlogout():
    response = make_response(redirect(url_for('login')))

    # delete token cookie
    response.set_cookie(
        'token',
        '',
        expires=0,
        httponly=True
    )

    return response


# --------------------------------Checkout & Payment Routes --------------------------------#

# Checkout route - Display checkout page
@app.route('/user/checkout', methods=['GET', 'POST'])
@token_required(role='user')
def checkout():
    user = getUserByToken()
    
    if not user:
        return redirect(url_for('login'))
    
    user_id = user.get('userid')
    
    # Get cart items and total
    cart_items = get_cart_items_for_checkout(user_id)
    cart_total = get_cart_total_amount(user_id)
    
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('user_cart'))
    
    if request.method == 'POST':
        # Create Razorpay order
        try:
            razorpay_order = create_razorpay_order(
                amount=cart_total,
                order_description=f"Order for user {user_id}",
                key_id=RAZORPAY_KEY_ID,
                key_secret=RAZORPAY_KEY_SECRET
            )
            
            # Store order details in session for verification
            return render_template(
                'user/payment.html',
                razorpay_order=razorpay_order,
                cart_items=cart_items,
                cart_total=cart_total,
                user=user,
                razorpay_key=RAZORPAY_KEY_ID
            )
        except Exception as e:
            flash(f'Error creating order: {str(e)}', 'error')
            return redirect(url_for('user_cart'))
    
    return render_template(
        'user/checkout.html',
        cart_items=cart_items,
        cart_total=cart_total,
        user=user
    )


# Payment verification route
@app.route('/user/verify-payment', methods=['POST'])
@token_required(role='user')
def verify_payment_route():
    user = getUserByToken()
    
    if not user:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user_id = user.get('userid')
    data = request.get_json()
    
    try:
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')
        
        # Verify payment signature
        is_valid = verify_payment(payment_id, order_id, signature, RAZORPAY_KEY_SECRET)
        
        if is_valid:
            # Get cart items for order creation
            cart_items = get_cart_items_for_checkout(user_id)
            cart_total = get_cart_total_amount(user_id)
            
            # Create order in database
            order_created = create_order_in_db(
                user_id=user_id,
                order_id=order_id,
                payment_id=payment_id,
                cart_items=cart_items,
                total_amount=cart_total
            )
            
            if order_created:
                # Clear user's cart
                clear_user_cart(user_id)
                
                return jsonify({
                    'success': True,
                    'message': 'Payment verified and order created successfully',
                    'order_id': order_id
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Payment verified but order creation failed'
                }), 500
        else:
            return jsonify({
                'success': False,
                'message': 'Payment verification failed'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing payment: {str(e)}'
        }), 500


# Payment success page
@app.route('/user/payment-success/<order_id>')
@token_required(role='user')
def payment_success(order_id):
    return render_template('user/payment_success.html', order_id=order_id)


# Payment failed page
@app.route('/user/payment-failed')
@token_required(role='user')
def payment_failed():
    return render_template('user/payment_failed.html')

# main
if __name__ == "__main__":
    createTables()
    app.run(
        debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true',
        port=int(os.environ.get('PORT', 5009))
    )
    