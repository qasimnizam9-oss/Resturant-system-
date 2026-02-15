from app import app, db
from models import Category, MenuItem

def seed_database():
    with app.app_context():
        # 1. Clear everything to start fresh
        db.drop_all()
        db.create_all()

        # 2. Add Categories
        starters = Category(name="Starters")
        mains = Category(name="Main Course")
        desserts = Category(name="Desserts")
        db.session.add_all([starters, mains, desserts])
        db.session.commit()

        # 3. Add Professional Dishes
        dishes = [
            MenuItem(
                name="Grilled Atlantic Salmon",
                description="Fresh salmon fillet with lemon butter sauce and seasonal asparagus.",
                price=24.99,
                image_url="https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=500",
                category_id=mains.id
            ),
            MenuItem(
                name="Truffle Mushroom Pasta",
                description="Creamy tagliatelle with wild mushrooms and white truffle oil.",
                price=18.50,
                image_url="https://images.unsplash.com/photo-1473093226795-af9932fe5856?w=500",
                category_id=mains.id
            ),
            MenuItem(
                name="Molten Chocolate Cake",
                description="Warm dark chocolate cake with a gooey center and vanilla bean ice cream.",
                price=9.99,
                image_url="https://images.unsplash.com/photo-1624353339130-975003666f7d?w=500",
                category_id=desserts.id
            )
        ]

        db.session.add_all(dishes)
        db.session.commit()
        print("Success: Database seeded with professional dishes!")

if __name__ == "__main__":
    seed_database()