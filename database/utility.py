from database.connection import databaseConfig


# check user exists or not
def checkUserExists(email:str):
    # database accesss
    db_config = databaseConfig()
    cursor = db_config.cursor()
    cursor.execute('select userid from users where email=?;', (email,))
    
    if cursor.fetchone():
        cursor.close()
        db_config.close()
        return True
    else:
        cursor.close()
        db_config.close()
        return False
    
# insert user data into db
def addUser(name: str, email: str, phone_number: str, password: str, profile_image: str = None):
    db = databaseConfig()
    cursor = db.cursor()

    query = """
        INSERT INTO users
        (name, email, phone_number, password, profile_image)
        VALUES (?, ?, ?, ?, ?)
    """

    cursor.execute(query, (name, email, phone_number, password, profile_image))
    db.commit()
    cursor.close()
    db.close()

    

# get password and role form database
def getUserDetails(email:str, role:str=None):
    # database accesss
    db_config = databaseConfig()
    cursor = db_config.cursor()
    user_details_query = "select userid, password, role from users where email = ?"
    if role:
        user_details_query =  "select userid, password, role from users where email = ? and role = ?"
        cursor.execute(user_details_query, (email,role))
    else:
        cursor.execute(user_details_query, (email,))
    data = cursor.fetchone()
    cursor.close()
    db_config.close()
    return dict(data) if data else None

# get user details by id
def getUserDetailsByID(userid:int, role:str=None):
    # database accesss
    db_config = databaseConfig()
    cursor = db_config.cursor()
    user_details_query = "select * from users where userid = ?"
    
    cursor.execute(user_details_query, (userid,))
    user = cursor.fetchone()
    cursor.close()
    db_config.close()
    return dict(user) if user else None


## Get all categories from database
def getCatagoriesFromDB():
    db_config = databaseConfig()
    cursor = db_config.cursor()
    cursor.execute('select distinct(category) from products;')
    category_list = cursor.fetchall()
    for i in range(len(category_list)):
        category_list[i] = category_list[i][0]
    cursor.close()
    db_config.close()
    return category_list


## Get all products from database
def getProductsFromDB(name='', category='', status=''):
    db = databaseConfig()
    cursor = db.cursor()
    query = "SELECT * FROM products WHERE 1=1"
    values = []
    # Filter by product name
    if name:
        query += " AND name LIKE ?" 
        values.append(f"%{name}%")
    # Filter by category
    if category:
        
        query += " AND category = ?"
        values.append(category)
        
    # Filter by status
    if status:
        query += " AND active = ?"
        values.append(status)
    cursor.execute(query, values)
    products = cursor.fetchall()
    cursor.close()
    db.close()
    return [dict(p) for p in products]




def addProductToDB(name, description, category, price, stock, active, image_url=None):
    db = databaseConfig()
    cursor = db.cursor()

    product_insert_query = """
        INSERT INTO products
        (name, description, category, image_url, price, stock, active)
        VALUES (?,?,?,?,?,?,?)
    """

    cursor.execute(product_insert_query, (name, description, category, image_url, price, stock, active))

    db.commit()
    cursor.close()
    db.close()


## Total Orders-----------------------------------------
def totalOrdersCount():
    db = databaseConfig()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM orders;")
    orders_count = cursor.fetchone()[0]

    cursor.close()
    db.close()
    return orders_count

# get orders --------------------------------------------------
def getOrders(orderid:int = "", product_name:str= "", from_date='', to_date = ""):
    db = databaseConfig()
    cursor = db.cursor()

    query = """select order_id, product_name, order_status, total_price, created_at 
    from orders where 1=1"""
    values = []
    if orderid:
        query += " and order_id= ?"
        values.append(orderid)
    if product_name:
        query += " and product_name like ?"
        values.append(f"%{product_name}%")
    if from_date:
        query += " and created_at > ?"
        values.append(from_date)
    if to_date:
        query += " and created_at < ?"
        values.append(to_date)
    query += " Order by created_at desc;"
    cursor.execute(query, values)
    orders = cursor.fetchall()
    cursor.close()
    db.close()
    return [dict(o) for o in orders]


def toggleProduct(pid, status):
    db = databaseConfig()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE products SET active=? WHERE productid=?",
        (status, pid)
    )

    db.commit()
    cursor.close()
    db.close()


# get users info -------------------------------------------------------
def usersDetails(name:str, email:str,role:str='user'):
    db = databaseConfig()
    cursor = db.cursor()

    query = "SELECT userid, name, email, phone_number, role, created_at, profile_image FROM users WHERE 1=1"
    values = []

    if name:
        query += " AND name LIKE ?"
        values.append(f"%{name}%")

    if email:
        query += " AND email LIKE ?"
        values.append(f"%{email}%")

    if role:
        query += " AND role = ?"
        values.append(role)

    query += " ORDER BY created_at DESC"

    cursor.execute(query, values)
    users = cursor.fetchall()

    cursor.close()
    db.close()
    return [dict(u) for u in users]


# update admin profile in database-------------------------------------------
def updateAdminProfile(new_password:str,userid:int):
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute("""
            UPDATE users
            SET password=?
            WHERE userid=?
        """, (new_password, userid))
    db.commit()
    cursor.close()
    db.close()



# get product details bt id--------------------------------------------------
def getProductDetailsByID(productid:int):
    db = databaseConfig()
    cursor = db.cursor()

    # FETCH PRODUCT
    cursor.execute(
        "SELECT * FROM products WHERE productid = ?",
        (productid,)
    )
    product = cursor.fetchone()
    cursor.close()
    db.close()
    return dict(product) if product else None

# update product info in database
def updateProductInfo(name, description, category,price, stock, active, productid):
    db = databaseConfig()
    cursor = db.cursor()
    update_query = """
            UPDATE products SET name=?, description=?, category=?, price=?, stock=?, active=?
            WHERE productid=?
        """

    cursor.execute(update_query, (name, description, category, price, stock, active, productid))
    db.commit()
    cursor.close()
    db.close()
    return True

## Deactivate product in database
def updateProductStatus(productid, status:int=0):
    db = databaseConfig()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE products SET active = ? WHERE productid = ?",
        (status, productid)
    )
    db.commit()
    cursor.close()
    db.close()
    return True



## get view user
def viewUserByAdmin(userid):
    db = databaseConfig()
    cursor = db.cursor()

    cursor.execute(
        "SELECT userid, name, email, role, status, created_at "
        "FROM users WHERE userid = ?",
        (userid,)
    )

    user = cursor.fetchone()

    cursor.close()
    db.close()
    return dict(user) if user else None


# ==================== CART FUNCTIONS ====================

# Add item to cart
def addToCart(user_id, product_id, quantity=1):
    db = databaseConfig()
    cursor = db.cursor()
    
    # Get product details
    cursor.execute("SELECT name, price, image_url FROM products WHERE productid = ?", (product_id,))
    product = cursor.fetchone()
    
    if not product:
        cursor.close()
        db.close()
        return False
    
    product = dict(product)
    
    # Check if item already exists in cart
    cursor.execute(
        "SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    )
    existing_item = cursor.fetchone()
    
    if existing_item:
        # Update quantity if item exists
        new_quantity = existing_item[0] + quantity
        cursor.execute(
            "UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?",
            (new_quantity, user_id, product_id)
        )
    else:
        # Insert new item
        cursor.execute(
            """INSERT INTO cart 
            (user_id, product_id, product_name, product_price, quantity, image_url)
            VALUES (?, ?, ?, ?, ?, ?)""",
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
    
    query = """
        SELECT cart_id, product_id, product_name, product_price, quantity, image_url,
               (product_price * quantity) as total_price
        FROM cart
        WHERE user_id = ?
        ORDER BY created_at DESC
    """
    
    cursor.execute(query, (user_id,))
    items = cursor.fetchall()
    
    cursor.close()
    db.close()
    return [dict(item) for item in items]


# Remove item from cart
def removeFromCart(cart_id, user_id):
    db = databaseConfig()
    cursor = db.cursor()
    
    cursor.execute(
        "DELETE FROM cart WHERE cart_id = ? AND user_id = ?",
        (cart_id, user_id)
    )
    
    db.commit()
    cursor.close()
    db.close()
    return True


# Update cart item quantity
def updateCartQuantity(cart_id, user_id, quantity):
    db = databaseConfig()
    cursor = db.cursor()
    
    if quantity <= 0:
        # Remove item if quantity is 0 or less
        return removeFromCart(cart_id, user_id)
    
    cursor.execute(
        "UPDATE cart SET quantity = ? WHERE cart_id = ? AND user_id = ?",
        (quantity, cart_id, user_id)
    )
    
    db.commit()
    cursor.close()
    db.close()
    return True


# Clear all cart items for a user
def clearCart(user_id):
    db = databaseConfig()
    cursor = db.cursor()
    
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    
    db.commit()
    cursor.close()
    db.close()
    return True


# Get cart total
def getCartTotal(user_id):
    db = databaseConfig()
    cursor = db.cursor()
    
    cursor.execute(
        """SELECT SUM(product_price * quantity) as total
        FROM cart
        WHERE user_id = ?""",
        (user_id,)
    )
    
    result = cursor.fetchone()
    cursor.close()
    db.close()
    
    return result[0] if result and result[0] else 0               