from inventory_app import create_app
from inventory_app.extensions import db
from inventory_app.models import Item, Unit, AssetTransaction, User
from datetime import datetime, timedelta

def add_compatible_unit():
    app = create_app()
    with app.app_context():
        print("Menambahkan unit dengan SN yang kompatibel...")
        
        # Cari item Lighting yang sudah ada
        item = Item.query.filter_by(category='Lighting').first()
        if not item:
            item = Item(name='Lighting Visualizer', category='Lighting', description='Lampu panggung')
            db.session.add(item)
            db.session.commit()
        
        # Tambah unit A-703 dengan status Rented agar bisa di-check in
        existing = Unit.query.filter_by(serial_number='A-703').first()
        if existing:
            print(f"Unit A-703 sudah ada dengan status: {existing.status}")
            # Ubah status ke Rented jika belum
            if existing.status != 'Rented':
                existing.status = 'Rented'
                db.session.commit()
                print("Status diubah ke 'Rented' untuk testing Barang Masuk")
        else:
            unit = Unit(
                item_id=item.id,
                serial_number='A-703',
                status='Rented',  # Set Rented agar muncul di Barang Masuk
                last_check_in=datetime.utcnow() - timedelta(days=5)
            )
            db.session.add(unit)
            db.session.flush()
            
            # Tambah transaksi OUT agar ada history
            admin = User.query.first()
            trans = AssetTransaction(
                unit_id=unit.id,
                type='OUT',
                notes='Event: Testing @ Gudang',
                admin_id=admin.id if admin else None,
                timestamp=datetime.utcnow() - timedelta(hours=12)
            )
            db.session.add(trans)
            db.session.commit()
            print("Unit A-703 berhasil ditambahkan dengan status 'Rented'")
        
        print("\nSekarang Anda bisa scan QR 'A-703' di halaman Barang Masuk!")

if __name__ == "__main__":
    add_compatible_unit()
