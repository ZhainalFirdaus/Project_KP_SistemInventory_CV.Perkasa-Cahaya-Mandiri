from app import app
from inventory_app.extensions import db
from inventory_app.models import User, AssetTransaction, Unit, Item
from datetime import datetime

def test_integrity():
    with app.app_context():
        print("--- Testing Database Integrity ---")
        
        # 1. Check User
        user = User.query.first()
        if not user:
            print("(!) No users found. Skipping transaction check.")
            return
        print(f"User check: Found '{user.username}'")
        
        # 2. Check Item & Unit
        unit = Unit.query.first()
        if not unit:
            print("(!) No units found. Skipping transaction link check.")
            return
        print(f"Unit check: Found '{unit.serial_number}' for item '{unit.item.name}'")
        
        # 3. Create a Dummy Transaction with current_user logic simulation
        try:
            test_notes = "Verification Test Record"
            new_trans = AssetTransaction(
                unit_id=unit.id,
                type='IN',
                notes=test_notes,
                admin_id=user.id
            )
            db.session.add(new_trans)
            db.session.commit()
            print("Transaction creation: SUCCESS")
            
            # Verify Relationship
            fetched_trans = AssetTransaction.query.filter_by(notes=test_notes).first()
            if fetched_trans and fetched_trans.admin:
                print(f"Relationship check: SUCCESS (Linked to admin: {fetched_trans.admin.username})")
            else:
                print("Relationship check: FAILED (admin name not accessible)")
            
            # Cleanup
            db.session.delete(fetched_trans)
            db.session.commit()
            print("Cleanup: SUCCESS")
            
        except Exception as e:
            print(f"Error during integrity test: {e}")
            db.session.rollback()

if __name__ == "__main__":
    test_integrity()
