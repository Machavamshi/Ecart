"""
Script to add product images to the database
Maps existing product images to products in the database
"""

from database.connection import databaseConfig

# Product image mapping - maps product names to their images
product_image_mapping = {
    'Laptop': 'uploads/products/macbook.jpg',
    'Wireless Mouse': 'uploads/products/mouse.jpg',
    'USB-C Charger': 'uploads/products/charger.jpg',
    'Desk Lamp': 'uploads/products/sony_tv.jpg',
    'Mechanical Keyboard': 'uploads/products/keyboard.jpg',
    'Monitor Stand': 'uploads/products/dell_desktop.jpg',
    'Webcam 1080p': 'uploads/products/canon_dslr.jpg',
    'Desk Organizer': 'uploads/products/backpack.jpg',
    'Portable SSD 1TB': 'uploads/products/harddrive.jpg',
    'USB Hub': 'uploads/products/powerbank.jpg',
    'Notebook Set': 'uploads/products/sony_headphones.jpg',
    'Pen Set': 'uploads/products/boat_earphones.jpg',
    'Desk Pad': 'uploads/products/wired_earphones.jpg',
    'Phone Stand': 'uploads/products/iphone14.jpg',
    'Cable Organizer': 'uploads/products/airpods.jpg',
}


def update_product_images():
    """Update product images in the database"""
    try:
        db = databaseConfig()
        cursor = db.cursor()
        
        count = 0
        for product_name, image_path in product_image_mapping.items():
            # Update product with image
            cursor.execute(
                "UPDATE products SET image_url = ? WHERE name = ?",
                (image_path, product_name)
            )
            
            if cursor.rowcount > 0:
                count += 1
                print(f"✓ Updated: {product_name} → {image_path.split('/')[-1]}")
            else:
                print(f"✗ Product not found: {product_name}")
        
        db.commit()
        cursor.close()
        db.close()
        
        print(f"\n✓ Successfully updated {count} products with images!")
        return True
    
    except Exception as e:
        print(f"✗ Error updating product images: {str(e)}")
        return False


def list_available_images():
    """List all available product images"""
    import os
    uploads_dir = os.path.join('static', 'uploads', 'products')
    
    if os.path.exists(uploads_dir):
        images = os.listdir(uploads_dir)
        print(f"Available images ({len(images)}):")
        for img in sorted(images):
            print(f"  - {img}")
        return images
    else:
        print(f"Upload directory not found: {uploads_dir}")
        return []


if __name__ == "__main__":
    print("=" * 60)
    print("Product Image Assignment Script")
    print("=" * 60)
    print()
    
    print("Available Product Images:")
    print("-" * 60)
    list_available_images()
    
    print()
    print("Assigning images to products...")
    print("-" * 60)
    update_product_images()
    print()
    print("=" * 60)
