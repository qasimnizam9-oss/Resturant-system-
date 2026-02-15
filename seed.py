from app import app, db
from models import Category, MenuItem

def seed_data():
    with app.app_context():
        # Clear existing data to avoid duplicates
        db.drop_all()
        db.create_all()

        # 1. Create Categories
        starters = Category(name="Starters")
        mains = Category(name="Main Course")
        desserts = Category(name="Desserts")
        db.session.add_all([starters, mains, desserts])
        db.session.commit()

        # 2. Add Professional Dishes
        items = [
            MenuItem(
                name="Truffle Mushroom Arancini",
                description="Crispy risotto balls stuffed with mozzarella and truffle oil.",
                price=12.50,
                image_url="https://images.unsplash.com/photo-1541529086526-db283c563270?w=500",
                category_id=starters.id
            ),
            MenuItem(
                name="Pan-Seared Sea Bass",
                description="Fresh sea bass served with lemon butter sauce and asparagus.",
                price=28.00,
                image_url="https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=500",
                category_id=mains.id
            ),
            MenuItem(
                name="Classic Ribeye Steak",
                description="Dry-aged beef served with garlic mash and red wine reduction.",
                price=34.99,
                image_url="https://images.unsplash.com/photo-1546241072-48010ad28c2c?w=500",
                category_id=mains.id
            ),
            MenuItem(
                name="Molten Lava Cake",
                description="Dark chocolate cake with a gooey center and vanilla bean ice cream.",
                price=9.00,
                image_url="https://images.unsplash.com/photo-1624353339130-975003666f7d?w=500",
                category_id=desserts.id
            )
        ]
        
        db.session.add_all(items)
        db.session.commit()
        print("Database seeded with professional dishes!")

if __name__ == '__main__':
    seed_data()