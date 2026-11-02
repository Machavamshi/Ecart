from flask import Flask, render_template, redirect, url_for, request, make_response,flash

import jwt
from datetime import datetime, timedelta, timezone

from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename


# ------------import database logics -------------------
from database.tables import createTables
from database.utility import checkUserExists, addUser, getUserDetails, getCatagoriesFromDB, getProductsFromDB
from database.utility import addProductToDB, orderdCount, getOrders
app = Flask(__name__)
app.config['SECRET_KEY'] = "srinubabu@123"






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






# index route
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
    return render_template('login.html')


# ---------------------- images upload path ------------------
UPLOAD_FOLDER = 'static/uploads/profile'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# ------------------------------------------------------------
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

    return render_template('register.html')

# forgotpassword route
@app.route('/forgotpassword')
def forgotpassword():
    return "forgot Password Page"



## Admin Routes
# admin dashborad route
@app.route('/admin')
@token_required(role='admin')
def admin():
    return render_template('admin.html')

# product route

@app.route('/admin/products')
@token_required(role='admin')
def products():
    # get all categories name 
    categories = getCatagoriesFromDB()

    product_name = request.args.get('name',"")
    category = request.args.get('category', "")
    status = request.args.get('status', "")

    print(category, product_name, status)
    # Get all products from  database
    products = getProductsFromDB(name=product_name, category= category, status= status)
    # print(products[:3])
    return render_template('products.html', categories= categories, products=products)

# Add product Route

@app.route('/admin/addproduct', methods = ['GET','POST'])
@token_required(role='admin')
def addproduct():
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
                image_url = os.path.join('uploads', filename).replace('\\', '/')
            else:
                flash("Invalid image format")
                return redirect(url_for('addproduct'))

        # add products details into products table (include image_url if present)
        addProductToDB(name=name,
                       description=description,
                       category=category,
                       price=price,
                       stock=stock,
                       active=active,
                       image_url=image_url)
        flash("Product added successfully","success")
        return redirect(url_for('products')) # after redirect to products page

    return render_template('addproduct.html')

# Delete product Route

@app.route('/admin/users')
@token_required(role='admin')
def adminusers():
    return "admin Users"

@app.route('/admin/deleteproduct/<int:productid>')
@token_required(role='admin')
def deleteproductWithId(productid):
    return "Delete product page"

# orders Route

@app.route('/admin/orders')
@token_required(role='admin')
def orders():
    # get filter parameter 
    orderid = request.args.get('orderid',"")
    product_name = request.args.get('productname',"")
    from_date = request.args.get('fromdate',"")
    to_date = request.args.get('todate',"")

    orders_count = orderdCount()
    # getting filterd orders
    orders = getOrders(orderid=orderid,
                       product_name=product_name,
                       from_date=from_date,
                       to_date=to_date)
    filter_orders_count = len(orders)
    print(orders[:3])

    return render_template('adminorders.html',
                            total_orders = orders_count,
                            filtred_order_count=filter_orders_count,
                            orders=orders)




# admin profilee route
@app.route('/admin/profile')
@token_required(role='admin')
def profile():
    return "admin profile page"

from flask import redirect, url_for, make_response

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
@token_required(role='user')
@app.route('/user')
def user():
    return render_template('user.html')

#home route
@token_required(role='user')
@app.route('/user/home')
def user_home():
    return "user home page"

# categories route
@token_required(role='user')
@app.route('/user/categories')
def user_categories():
    return "User categories page"

# users orders route
@token_required(role='user')
@app.route('/users/orders')
def user_orders():
    return "Users orders page"

# cart route
@token_required(role='user')
@app.route('/user/cart')
def user_cart():
    return "user cart page"

# user profile route
@token_required(role='user')
@app.route('/user/profile')
def user_profile():
    return "user profile page"



# main
if __name__ == "__main__":
    createTables()
    app.run(debug=True, port=5006)
    