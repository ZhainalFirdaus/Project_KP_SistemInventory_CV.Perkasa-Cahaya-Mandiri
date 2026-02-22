from app import create_app
from inventory_app.extensions import db
from inventory_app.models import User, Item, Unit, AssetTransaction, ActivityLog
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def seed_data():
    app = create_app()
    with app.app_context():
        print("Mulai pembuatan data dummy...")
        
        # 1. Pastikan Admin ada
        admin = User.query.filter_by(username='admin123').first()
        if not admin:
            admin = User(
                username='admin123',
                password_hash=generate_password_hash('admin123'),
                image_file='default_user.jpg'
            )
            db.session.add(admin)
            db.session.commit()
            print("- User admin dibuat (user: admin123, pass: admin123)")
        else:
            print("- User admin sudah ada.")

        # 2. Tambah Items
        items_data = [
            {'name': 'Moving Head Sharpy 230W', 'category': 'Lighting', 'desc': 'Beam lighting for professional stage.'},
            {'name': 'Line Array RCF HDL 20-A', 'category': 'Audio', 'desc': 'High performance active line array module.'},
            {'name': 'LED Video Wall P3.9', 'category': 'Multimedia', 'desc': 'Indoor LED screen panels for events.'},
            {'name': 'Digital Mixer Midas M32', 'category': 'Audio', 'desc': 'Standard digital console for FOH.'},
            {'name': 'Smoke Machine 1500W', 'category': 'Lighting', 'desc': 'Professional fog generator.'}
        ]

        created_items = []
        for it in items_data:
            existing_item = Item.query.filter_by(name=it['name']).first()
            if not existing_item:
                item = Item(name=it['name'], category=it['category'], description=it['desc'])
                db.session.add(item)
                created_items.append(item)
            else:
                created_items.append(existing_item)
        
        db.session.commit()
        print(f"- {len(items_data)} Kategori Barang siap.")

        # 3. Tambah Units
        statuses = ['Ready', 'Rented', 'Maintenance']
        locations = ['Gedung A', 'Aula Utama', 'Lapangan Outdoor', 'Hotel Mulia']
        
        unit_count = 0
        for item in created_items:
            # Buat 3-5 unit per item
            num_units = random.randint(3, 5)
            for i in range(1, num_units + 1):
                sn = f"{item.name[:3].upper()}-{random.randint(100, 999)}-{i:02d}"
                existing_unit = Unit.query.filter_by(serial_number=sn).first()
                if not existing_unit:
                    status = random.choice(statuses)
                    unit = Unit(
                        item_id=item.id,
                        serial_number=sn,
                        status=status,
                        last_check_in=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                    )
                    db.session.add(unit)
                    db.session.flush() # Get ID for transaction

                    # 4. Tambah Transaksi History (jika status Rented/Maintenance)
                    if status != 'Ready':
                        trans_type = 'OUT' if status == 'Rented' else 'IN'
                        notes = f"Event: {random.choice(locations)} @ Jakarta" if status == 'Rented' else 'Maintenance: Perbaikan kabel/fader'
                        
                        trans = AssetTransaction(
                            unit_id=unit.id,
                            type=trans_type,
                            notes=notes,
                            admin_id=admin.id,
                            timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                        )
                        db.session.add(trans)
                    
                    unit_count += 1
        
        db.session.commit()
        print(f"- {unit_count} Unit alat berhasil ditambahkan.")
        
        # 5. Activity Log
        log = ActivityLog(
            user_id=admin.id,
            action='SEED_DATA',
            details='Melakukan pengisian data dummy awal sistem.',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        print("\nSUKSES: Data dummy berhasil dimasukkan!")
        print("Silakan buka Dashboard untuk melihat hasilnya.")

if __name__ == "__main__":
    seed_data()
