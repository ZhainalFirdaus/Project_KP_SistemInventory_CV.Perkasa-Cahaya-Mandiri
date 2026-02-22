from app import app, db, Item
with app.app_context():
    items = Item.query.all()
    print(f"{'ID':<5} {'Name':<30} {'Image File'}")
    print("-" * 50)
    for item in items:
        print(f"{item.id:<5} {item.name:<30} {item.image_file}")
