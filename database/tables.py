from database.connection import databaseConfig


# tables creation function defination
def createTables():
    db_config = databaseConfig()
    cursor = db_config.cursor()

    users_table_query = '''
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
    );'''

    cursor.execute(users_table_query)

    products_table_query = '''
    CREATE TABLE IF NOT EXISTS products (
        productid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL,
        image_url TEXT,
        price REAL NOT NULL,
        stock INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );'''

    cursor.execute(products_table_query)

    orders_table_query = '''
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
    );'''

    cursor.execute(orders_table_query)

    cart_table_query = '''
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
    );'''

    cursor.execute(cart_table_query)
    db_config.commit()
    cursor.close()
    db_config.close()
