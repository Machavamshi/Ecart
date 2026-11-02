import razorpay
from database.connection import databaseConfig
from datetime import datetime


# Initialize Razorpay client (API keys should be in environment or config)
def get_razorpay_client(key_id: str, key_secret: str):
    """
    Initialize and return Razorpay client with API credentials
    """
    return razorpay.Client(auth=(key_id, key_secret))


# Create order in Razorpay
def create_razorpay_order(amount: float, order_description: str = "E-commerce Order", key_id: str = None, key_secret: str = None):
    """
    Create an order in Razorpay
    Args:
        amount: Order amount in rupees (will be converted to paise)
        order_description: Description of the order
        key_id: Razorpay API Key ID
        key_secret: Razorpay Key Secret
    Returns:
        dict: Razorpay order response
    """
    if not key_id or not key_secret:
        raise ValueError("Razorpay API keys are required. Please configure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET environment variables.")
    
    client = get_razorpay_client(key_id, key_secret)
    
    ORDER_AMOUNT = int(amount * 100)  # Convert to paise
    
    order_data = {
        "amount": ORDER_AMOUNT,
        "currency": "INR",
        "receipt": f"order_receipt_{datetime.now().timestamp()}",
        "description": order_description
    }
    
    order = client.order.create(data=order_data)
    return order


# Create order in database after successful payment
def create_order_in_db(user_id: int, order_id: str, payment_id: str, cart_items: list, total_amount: float):
    """
    Create order records in database after payment verification
    Args:
        user_id: User ID
        order_id: Razorpay Order ID
        payment_id: Razorpay Payment ID
        cart_items: List of cart items with product details
        total_amount: Total order amount
    """
    db = databaseConfig()
    cursor = db.cursor()
    
    try:
        for item in cart_items:
            insert_query = """
                INSERT INTO orders 
                (order_id, user_id, product_id, product_name, product_price, quantity, total_price, order_status, payment_method, payment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            item_total = float(item['product_price']) * int(item['quantity'])
            
            cursor.execute(insert_query, (
                order_id,
                user_id,
                item['product_id'],
                item['product_name'],
                float(item['product_price']),
                int(item['quantity']),
                item_total,
                'PENDING',  # order_status
                'RAZORPAY',  # payment_method
                'SUCCESS'    # payment_status (since we verified payment)
            ))
        
        db.commit()
        cursor.close()
        db.close()
        return True
    
    except Exception as e:
        print(f"Error creating order in database: {str(e)}")
        db.rollback()
        cursor.close()
        db.close()
        return False


# Clear user's cart after order creation
def clear_user_cart(user_id: int):
    """
    Clear all items from user's cart after successful order
    """
    db = databaseConfig()
    cursor = db.cursor()
    
    try:
        delete_query = "DELETE FROM cart WHERE user_id = ?"
        cursor.execute(delete_query, (user_id,))
        db.commit()
        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f"Error clearing cart: {str(e)}")
        db.rollback()
        cursor.close()
        db.close()
        return False


# Verify payment with Razorpay
def verify_payment(payment_id: str, order_id: str, signature: str, key_secret: str):
    """
    Verify payment signature from Razorpay
    Args:
        payment_id: Razorpay Payment ID
        order_id: Razorpay Order ID
        signature: Razorpay Signature from webhook
        key_secret: Razorpay Key Secret
    Returns:
        bool: True if signature is valid, False otherwise
    """
    import hmac
    import hashlib
    
    # Reconstruct the data string
    data = f"{order_id}|{payment_id}"
    
    # Create expected signature
    expected_signature = hmac.new(
        key_secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    return expected_signature == signature


# Get user's cart items formatted for order creation
def get_cart_items_for_checkout(user_id: int):
    """
    Get cart items with all necessary details for checkout
    """
    db = databaseConfig()
    cursor = db.cursor()
    
    query = """
        SELECT cart_id, product_id, product_name, product_price, quantity, image_url
        FROM cart
        WHERE user_id = ?
    """
    
    cursor.execute(query, (user_id,))
    items = cursor.fetchall()
    cursor.close()
    db.close()
    
    return [dict(item) for item in items]


# Calculate cart total
def get_cart_total_amount(user_id: int):
    """
    Calculate total amount for user's cart
    """
    db = databaseConfig()
    cursor = db.cursor()
    
    query = """
        SELECT SUM(product_price * quantity) as total
        FROM cart
        WHERE user_id = ?
    """
    
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    
    total = result[0] if result and result[0] else 0
    return float(total)   