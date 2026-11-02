

from database.connection import databaseConfig

# users orders page ___________________

def view_users_orders(user_id):
    db = databaseConfig()
    cursor = db.cursor()

    query = """
        SELECT *
        FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
    """

    cursor.execute(query, (user_id,))
    orders = cursor.fetchall()

    cursor.close()
    db.close()

    return [dict(o) for o in orders]


#_______________show category__________________

def show_category(category):
    db = databaseConfig()
    cursor = db.cursor()

    query = "SELECT * FROM products WHERE category = ? AND active = 1"

    cursor.execute(query, (category,))
    items = cursor.fetchall()

    cursor.close()
    db.close()

    return [dict(item) for item in items]


#_________user profile details___________-

def user_profile_details(userid):
    db=databaseConfig()
    cursor=db.cursor()
    query="select * from users where userid=?"
    cursor.execute(query,(userid,))
    profile=cursor.fetchone()
    cursor.close()
    db.close()
    return dict(profile) if profile else None


def update_user_profile(userid, name=None, phone=None, profile_image=None):
    db = databaseConfig()
    cursor = db.cursor()

    # build dynamic query parts
    updates = []
    values = []

    if name is not None:
        updates.append("name=?")
        values.append(name)

    if phone is not None:
        updates.append("phone_number=?")
        values.append(phone)

    if profile_image is not None:
        updates.append("profile_image=?")
        values.append(profile_image)

    if not updates:
        cursor.close()
        db.close()
        return False

    query = "UPDATE users SET " + ", ".join(updates) + " WHERE userid=?"
    values.append(userid)

    cursor.execute(query, tuple(values))
    db.commit()
    cursor.close()
    db.close()
    return True         










