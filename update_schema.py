from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Check if column exists by trying to select it (or just try to add it and catch error)
        # Using MySQL syntax
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE item ADD COLUMN image_file VARCHAR(100) DEFAULT 'default.jpg'"))
            conn.commit()
        print("Successfully added image_file column.")
    except Exception as e:
        print(f"Column might already exist or error: {e}")
