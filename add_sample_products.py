"""
Script to add sample products to the database
Run this to populate the database with test products
"""

from database.connection import databaseConfig
from database.utility import addProductToDB

# Sample products data
sample_products = [
    {
        "name": "Laptop",
        "description": "High-performance 15-inch laptop with Intel i7 processor, 16GB RAM, and 512GB SSD",
        "category": "Electronics",
        "price": 89999.00,
        "stock": 15,
        "active": 1,
    },
    {
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse with 2.4GHz receiver, long battery life, and precision tracking",
        "category": "Electronics",
        "price": 1299.00,
        "stock": 50,
        "active": 1,
    },
    {
        "name": "USB-C Charger",
        "description": "Fast 65W USB-C charger compatible with laptops, tablets, and phones",
        "category": "Electronics",
        "price": 1999.00,
        "stock": 40,
        "active": 1,
    },
    {
        "name": "Desk Lamp",
        "description": "LED desk lamp with adjustable brightness and color temperature, USB powered",
        "category": "Office",
        "price": 2499.00,
        "stock": 25,
        "active": 1,
    },
    {
        "name": "Mechanical Keyboard",
        "description": "RGB mechanical keyboard with Cherry MX switches, programmable keys, and aluminum frame",
        "category": "Electronics",
        "price": 7999.00,
        "stock": 20,
        "active": 1,
    },
    {
        "name": "Monitor Stand",
        "description": "Adjustable monitor stand with storage drawer, supports up to 30-inch displays",
        "category": "Office",
        "price": 3499.00,
        "stock": 30,
        "active": 1,
    },
    {
        "name": "Webcam 1080p",
        "description": "Full HD 1080p webcam with auto-focus, built-in microphone, and wide-angle lens",
        "category": "Electronics",
        "price": 3999.00,
        "stock": 35,
        "active": 1,
    },
    {
        "name": "Desk Organizer",
        "description": "Multi-compartment desk organizer made from sustainable bamboo",
        "category": "Office",
        "price": 899.00,
        "stock": 60,
        "active": 1,
    },
    {
        "name": "Portable SSD 1TB",
        "description": "Ultra-fast portable SSD with 1TB storage, USB 3.1 interface, and compact design",
        "category": "Electronics",
        "price": 8999.00,
        "stock": 18,
        "active": 1,
    },
    {
        "name": "USB Hub",
        "description": "7-port USB 3.0 hub with individual switches and power adapter",
        "category": "Electronics",
        "price": 1699.00,
        "stock": 45,
        "active": 1,
    },
    {
        "name": "Notebook Set",
        "description": "Set of 3 premium quality notebooks with lined pages, ideal for professionals",
        "category": "Stationery",
        "price": 499.00,
        "stock": 100,
        "active": 1,
    },
    {
        "name": "Pen Set",
        "description": "Premium ballpoint pen set with smooth writing experience and elegant design",
        "category": "Stationery",
        "price": 599.00,
        "stock": 80,
        "active": 1,
    },
    {
        "name": "Desk Pad",
        "description": "Large extended mouse pad (800x300mm) with non-slip base and smooth surface",
        "category": "Office",
        "price": 1299.00,
        "stock": 55,
        "active": 1,
    },
    {
        "name": "Phone Stand",
        "description": "Adjustable phone stand compatible with all smartphones, foldable design",
        "category": "Accessories",
        "price": 599.00,
        "stock": 75,
        "active": 1,
    },
    {
        "name": "Cable Organizer",
        "description": "Silicone cable organizer clips to keep desk cables neat and organized",
        "category": "Accessories",
        "price": 299.00,
        "stock": 120,
        "active": 1,
    },
]


def add_sample_products():
    """Add sample products to the database"""
    try:
        count = 0
        for product in sample_products:
            addProductToDB(
                name=product["name"],
                description=product["description"],
                category=product["category"],
                price=product["price"],
                stock=product["stock"],
                active=product["active"],
            )
            count += 1
            print(f"✓ Added: {product['name']}")
        
        print(f"\n✓ Successfully added {count} products to the database!")
        return True
    
    except Exception as e:
        print(f"✗ Error adding products: {str(e)}")
        return False


if __name__ == "__main__":
    print("Adding sample products to the database...\n")
    add_sample_products()
