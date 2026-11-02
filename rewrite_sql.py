from pathlib import Path

base = Path(r'c:\Users\siddu\OneDrive\Desktop\Ecommerce 2\database')
files = {
    'tables.py': """from database.connection import databaseConfig


# tables creation function defination
def createTables():
    db_config = databaseConfig()
    cursor = db_config.cursor()

    users_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        userid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone_number TEXT UNIQUE,
        password TEXT NOT NULL,
        profile_image TEXT,
        role TEXT DEFAULT 'user',
        status INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );"""

    cursor.execute(users_table_query)

    products_table_query = """
    CREATE TABLE IF NOT EXISTS products (
        productid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL,
        image_url TEXT,
        price REAL NOT NULL CHECK(price >= 0),
        stock INTEGER DEFAULT 0 CHECK(stock >= 0),
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );"""

    cursor.execute(products_table_query)

    orders_table_query = """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        product_price REAL NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        total_price REAL NOT NULL,
        order_status TEXT DEFAULT 'PENDING',
        payment_method TEXT,
        payment_status TEXT DEFAULT 'PENDING',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );"""

    cursor.execute(orders_table_query)

    cart_table_query = """
    CREATE TABLE IF NOT EXISTS cart (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        product_price REAL NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        image_url TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(userid),
        FOREIGN KEY (product_id) REFERENCES products(productid),
        UNIQUE(user_id, product_id)
    );"""

    cursor.execute(cart_table_query)
    db_config.commit()
    cursor.close()
    db_config.close()
""",
    'utility.py': """from database.connection import databaseConfig


# check user exists or not
def checkUserExists(email: str):
    db_config = databaseConfig()
    cursor = db_config.cursor()
    cursor.execute('SELECT userid FROM users WHERE email = ?;', (email,))
    exists = cursor.fetchone() is not None
    cursor.close()
    db_config.close()
    return exists


# insert user data into db
def addUser(name: str, email: str, phone_number: str, password: str, profile_image: str = None):
    db = databaseConfig()
    cursor = db.cursor()

    query = '''
        INSERT INTO users
        (name, email, phone_number, password, profile_image)
        VALUES (?, ?, ?, ?, ?)
    '''

    cursor.execute(query, (name, email, phone_number, password, profile_image))
    db.commit()
    cursor.close()
    db.close()


# get password and role from database
def getUserDetails(email: str, role: str = None):
    db_config = databaseConfig()
    cursor = db_config.cursor()
    user_details_query = 'SELECT userid, password, role FROM users WHERE email = ?;'

    if role:
        user_details_query = 'SELECT userid, password, role FROM users WHERE email = ? AND role = ?'
        cursor.execute(user_details_query, (email, role))
    else:
        cursor.execute(user_details_query, (email,))

    row = cursor.fetchone()
    data = dict(row) if row else None
    cursor.close()
    db_config.close()
    return data


# get user details by id
def getUserDetailsByID(userid: int, role: str = None):
    db_config = databaseConfig()
    cursor = db_config.cursor()
    user_details_query = 'SELECT * FROM users WHERE userid = ?;'
    cursor.execute(user_details_query, (userid,))
    row = cursor.fetchone()
    user = dict(row) if row else None
    cursor.close()
    db_config.close()
    return user


## Get all categories from database
def getCatagoriesFromDB():
    db_config = databaseConfig()
    cursor = db_config.cursor()
    cursor.execute('SELECT DISTINCT(category) FROM products;')
    category_list = [row[0] for row in cursor.fetchall()]
    cursor.close()
    db_config.close()
    return category_list


## Get all products from database
def getProductsFromDB(name='', category='', status=''):
    db = databaseConfig()
    cursor = db.cursor()
    query = 'SELECT * FROM products WHERE 1=1'
    values = []

    if name:
        query += ' AND name LIKE ?'
        values.append(f'%{name}%')

    if category:
        query += ' AND category = ?'
        values.append(category)

    if status:
        query += ' AND active = ?'
        values.append(status)

    cursor.execute(query, values)
    products = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return products


def addProductToDB(name, description, category, price, stock, active, image_url=None):
    db = databaseConfig()
    cursor = db.cursor()

    product_insert_query = '''
        INSERT INTO products
        (name, description, category, image_url, price, stock, active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''

    cursor.execute(product_insert_query, (name, description, category, image_url, price, stock, active))
    db.commit()
    cursor.close()
    db.close()


## Total Orders-----------------------------------------
def totalOrdersCount():
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM orders;')
    orders_count = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return orders_count


# get orders --------------------------------------------------
def getOrders(orderid: int = '', product_name: str = '', from_date='', to_date = ''):
    db = databaseConfig()
    cursor = db.cursor()

    query = '''SELECT order_id, product_name, order_status, total_price, created_at
    FROM orders WHERE 1=1'''
    values = []

    if orderid:
        query += ' AND order_id = ?'
        values.append(orderid)

    if product_name:
        query += ' AND product_name LIKE ?'
        values.append(f'%{product_name}%')

    if from_date:
        query += ' AND created_at > ?'
        values.append(from_date)

    if to_date:
        query += ' AND created_at < ?'
        values.append(to_date)

    query += ' ORDER BY created_at DESC;'
    cursor.execute(query, values)
    orders = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return orders


def toggleProduct(pid, status):
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute('UPDATE products SET active = ? WHERE productid = ?', (status, pid))
    db.commit()
    cursor.close()
    db.close()


# get users info -------------------------------------------------------
def usersDetails(name: str, email: str, role: str = 'user'):
    db = databaseConfig()
    cursor = db.cursor()

    query = 'SELECT userid, name, email, phone_number, role, created_at, profile_image FROM users WHERE 1=1'
    values = []

    if name:
        query += ' AND name LIKE ?'
        values.append(f'%{name}%')

    if email:
        query += ' AND email LIKE ?'
        values.append(f'%{email}%')

    if role:
        query += ' AND role = ?'
        values.append(role)

    query += ' ORDER BY created_at DESC'
    cursor.execute(query, values)
    users = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return users


# update admin profile in database-------------------------------------------
def updateAdminProfile(new_password: str, userid: int):
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET password = ? WHERE userid = ?', (new_password, userid))
    db.commit()
    cursor.close()
    db.close()


# get product details by id--------------------------------------------------
def getProductDetailsByID(productid: int):
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM products WHERE productid = ?', (productid,))
    product = cursor.fetchone()
    product = dict(product) if product else None
    cursor.close()
    db.close()
    return product


# update product info in database
def updateProductInfo(name, description, category, price, stock, active, productid):
    db = databaseConfig()
    cursor = db.cursor()
    update_query = '''
        UPDATE products SET name = ?, description = ?, category = ?, price = ?, stock = ?, active = ?
        WHERE productid = ?;
    '''

    cursor.execute(update_query, (name, description, category, price, stock, active, productid))
    db.commit()
    cursor.close()
    db.close()
    return True


## Deactivate product in database
def updateProductStatus(productid, status: int = 0):
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute('UPDATE products SET active = ? WHERE productid = ?', (status, productid))
    db.commit()
    cursor.close()
    db.close()
    return True


## get view user
def viewUserByAdmin(userid):
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute('SELECT userid, name, email, role, status, created_at FROM users WHERE userid = ?', (userid,))
    row = cursor.fetchone()
    user = dict(row) if row else None
    cursor.close()
    db.close()
    return user


# ==================== CART FUNCTIONS ====================

# Add item to cart
def addToCart(user_id, product_id, quantity=1):
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute('SELECT name, price, image_url FROM products WHERE productid = ?', (product_id,))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        db.close()
        return False

    product = dict(product)
    cursor.execute('SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    existing_item = cursor.fetchone()

    if existing_item:
        new_quantity = existing_item['quantity'] + quantity
        cursor.execute('UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?', (new_quantity, user_id, product_id))
    else:
        cursor.execute(
            'INSERT INTO cart (user_id, product_id, product_name, product_price, quantity, image_url) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, product_id, product['name'], product['price'], quantity, product['image_url'])
        )

    db.commit()
    cursor.close()
    db.close()
    return True


# Get all cart items for a user
def getCartItems(user_id):
    db = databaseConfig()
    cursor = db.cursor()
    query = '''
        SELECT cart_id, product_id, product_name, product_price, quantity, image_url,
               (product_price * quantity) as total_price
        FROM cart
        WHERE user_id = ?
        ORDER BY created_at DESC
    '''
    cursor.execute(query, (user_id,))
    items = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return items


# Remove item from cart
def removeFromCart(cart_id, user_id):
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute('DELETE FROM cart WHERE cart_id = ? AND user_id = ?', (cart_id, user_id))
    db.commit()
    cursor.close()
    db.close()
    return True


# Update cart item quantity
def updateCartQuantity(cart_id, user_id, quantity):
    db = databaseConfig()
    cursor = db.cursor()

    if quantity <= 0:
        return removeFromCart(cart_id, user_id)

    cursor.execute('UPDATE cart SET quantity = ? WHERE cart_id = ? AND user_id = ?', (quantity, cart_id, user_id))
    db.commit()
    cursor.close()
    db.close()
    return True


# Clear all cart items for a user
def clearCart(user_id):
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    db.commit()
    cursor.close()
    db.close()
    return True


# Get cart total
def getCartTotal(user_id):
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute('SELECT SUM(product_price * quantity) as total FROM cart WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result['total'] if result and result['total'] else 0
''',
    'user_utility.py': """from database.connection import databaseConfig

# users orders page ___________________

def view_users_orders(user_id):
    db = databaseConfig()
    cursor = db.cursor()

    query = '''
        SELECT *
        FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
    '''

    cursor.execute(query, (user_id,))
    orders = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return orders


# _______________show category__________________

def show_category(category):
    db = databaseConfig()
    cursor = db.cursor()

    query = 'SELECT * FROM products WHERE category = ? AND active = 1'
    cursor.execute(query, (category,))
    items = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return items


# _________user profile details___________-

def user_profile_details(userid):
    db = databaseConfig()
    cursor = db.cursor()
    query = 'SELECT * FROM users WHERE userid = ?'
    cursor.execute(query, (userid,))
    profile = cursor.fetchone()
    profile = dict(profile) if profile else None
    cursor.close()
    db.close()
    return profile


def update_user_profile(userid, name=None, phone=None, profile_image=None):
    db = databaseConfig()
    cursor = db.cursor()

    updates = []
    values = []

    if name is not None:
        updates.append('name = ?')
        values.append(name)

    if phone is not None:
        updates.append('phone_number = ?')
        values.append(phone)

    if profile_image is not None:
        updates.append('profile_image = ?')
        values.append(profile_image)

    if not updates:
        cursor.close()
        db.close()
        return False

    query = 'UPDATE users SET ' + ', '.join(updates) + ' WHERE userid = ?'
    values.append(userid)

    cursor.execute(query, tuple(values))
    db.commit()
    cursor.close()
    db.close()
    return True
''',
    'payment_utility.py': """import razorpay
from database.connection import databaseConfig
from datetime import datetime


# Initialize Razorpay client (API keys should be in environment or config)
def get_razorpay_client(key_id: str, key_secret: str):
    return razorpay.Client(auth=(key_id, key_secret))


# Create order in Razorpay
def create_razorpay_order(amount: float, order_description: str = 'E-commerce Order', key_id: str = None, key_secret: str = None):
    if not key_id or not key_secret:
        raise ValueError('Razorpay API keys are required. Please configure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET environment variables.')

    client = get_razorpay_client(key_id, key_secret)
    ORDER_AMOUNT = int(amount * 100)
    order_data = {
        'amount': ORDER_AMOUNT,
        'currency': 'INR',
        'receipt': f'order_receipt_{datetime.now().timestamp()}',
        'description': order_description
    }
    order = client.order.create(data=order_data)
    return order


# Create order in database after successful payment
def create_order_in_db(user_id: int, order_id: str, payment_id: str, cart_items: list, total_amount: float):
    db = databaseConfig()
    cursor = db.cursor()

    try:
        for item in cart_items:
            insert_query = '''
                INSERT INTO orders
                (order_id, user_id, product_id, product_name, product_price, quantity, total_price, order_status, payment_method, payment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            price = float(item['product_price'])
            quantity = int(item['quantity'])
            total_price = price * quantity
            cursor.execute(insert_query, (
                order_id,
                user_id,
                item['product_id'],
                item['product_name'],
                price,
                quantity,
                total_price,
                'PENDING',
                'RAZORPAY',
                'SUCCESS'
            ))

        db.commit()
        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f'Error creating order in database: {str(e)}')
        db.rollback()
        cursor.close()
        db.close()
        return False


# Clear user's cart after order creation
def clear_user_cart(user_id: int):
    db = databaseConfig()
    cursor = db.cursor()

    try:
        delete_query = 'DELETE FROM cart WHERE user_id = ?'
        cursor.execute(delete_query, (user_id,))
        db.commit()
        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f'Error clearing cart: {str(e)}')
        db.rollback()
        cursor.close()
        db.close()
        return False


# Verify payment with Razorpay
def verify_payment(payment_id: str, order_id: str, signature: str, key_secret: str):
    import hmac
    import hashlib
    data = f'{order_id}|{payment_id}'
    expected_signature = hmac.new(key_secret.encode(), data.encode(), hashlib.sha256).hexdigest()
    return expected_signature == signature


# Get user's cart items formatted for order creation
def get_cart_items_for_checkout(user_id: int):
    db = databaseConfig()
    cursor = db.cursor()

    query = '''
        SELECT cart_id, product_id, product_name, product_price, quantity, image_url
        FROM cart
        WHERE user_id = ?
    '''

    cursor.execute(query, (user_id,))
    items = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return items


# Calculate cart total
def get_cart_total_amount(user_id: int):
    db = databaseConfig()
    cursor = db.cursor()

    query = '''
        SELECT SUM(product_price * quantity) as total
        FROM cart
        WHERE user_id = ?
    '''

    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    db.close()

    total = result['total'] if result and result['total'] else 0
    return float(total)
'''
}

for name, content in files.items():
    path = base / name
    path.write_text(content, encoding='utf-8')
    print(f'Wrote {path}')
