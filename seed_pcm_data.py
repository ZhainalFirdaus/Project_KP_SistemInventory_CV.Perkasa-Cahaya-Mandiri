"""
Seed Dummy Data untuk CV. Perkasa Cahaya Mandiri
Kategori: Lighting, Audio, Multimedia, Stage Production, Power Generator
"""
from inventory_app import create_app
from inventory_app.extensions import db
from inventory_app.models import Item, Unit, AssetTransaction, ActivityLog, User
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def seed_pcm_data():
    app = create_app()
    with app.app_context():
        print("="*50)
        print("SEEDING DATA PCM RENTAL")
        print("="*50)
        
        # 1. Pastikan ada user admin
        admin = User.query.filter_by(username='admin123').first()
        if not admin:
            admin = User(username='admin123', password_hash=generate_password_hash('admin123'))
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created: admin123")
        
        # 2. Definisi produk berdasarkan kategori
        products = {
            'Lighting': [
                {'name': 'Moving Head Beam 230W', 'desc': 'Beam light untuk panggung'},
                {'name': 'Moving Head Spot 250W', 'desc': 'Spot light dengan gobo'},
                {'name': 'Par LED RGBW 54x3W', 'desc': 'Wash light LED'},
                {'name': 'Wash Moving Head 36x10W', 'desc': 'Wash light moving head'},
                {'name': 'Follow Spot 1200W', 'desc': 'Lampu sorot manual'},
            ],
            'Audio': [
                {'name': 'Line Array RCF HDL 10A', 'desc': 'Speaker line array aktif'},
                {'name': 'Digital Mixer Yamaha TF5', 'desc': 'Mixer digital 32 channel'},
                {'name': 'Subwoofer RCF SUB 8006', 'desc': 'Bass 18 inch dual driver'},
                {'name': 'Wireless Mic Shure ULXD', 'desc': 'Microphone wireless UHF'},
                {'name': 'Conference Mic Audio Technica', 'desc': 'Mic conference gooseneck'},
            ],
            'Multimedia': [
                {'name': 'LED Screen P3.9 Indoor', 'desc': 'LED videotron indoor'},
                {'name': 'LED Screen P4.8 Outdoor', 'desc': 'LED videotron outdoor'},
                {'name': 'Projector Panasonic 10K', 'desc': 'Projector DLP 10000 lumens'},
                {'name': 'Video Processor Novastar VX4S', 'desc': 'Processor LED display'},
            ],
            'Stage Production': [
                {'name': 'Truss Prolyte H30V 3M', 'desc': 'Truss aluminium 3 meter'},
                {'name': 'Stage Module 1x2M', 'desc': 'Panggung modular'},
                {'name': 'Backdrop Custom Print', 'desc': 'Cetak backdrop kustom'},
                {'name': 'Rigging Motor 1Ton', 'desc': 'Motor chain hoist'},
            ],
            'Power Generator': [
                {'name': 'Genset Silent 60 KVA', 'desc': 'Generator diesel silent'},
                {'name': 'Genset Silent 100 KVA', 'desc': 'Generator diesel medium'},
                {'name': 'Genset Silent 150 KVA', 'desc': 'Generator diesel besar'},
                {'name': 'UPS APC 3000VA', 'desc': 'Uninterruptible power supply'},
                {'name': 'Power Distribution Box 63A', 'desc': 'Panel listrik portable'},
            ]
        }
        
        # Prefix untuk serial number
        prefixes = {
            'Lighting': 'LGT',
            'Audio': 'AUD',
            'Multimedia': 'MUL',
            'Stage Production': 'STG',
            'Power Generator': 'PWR'
        }
        
        statuses = ['Ready', 'Rented', 'Maintenance']
        locations = ['Gedung A', 'Aula Utama', 'Lapangan Outdoor', 'Hotel Mulia', 'JIEXPO Kemayoran']
        
        total_items = 0
        total_units = 0
        
        for category, items in products.items():
            print(f"\n[+] Kategori: {category}")
            prefix = prefixes[category]
            
            for item_data in items:
                # Cek atau buat item
                item = Item.query.filter_by(name=item_data['name']).first()
                if not item:
                    item = Item(
                        name=item_data['name'],
                        category=category,
                        description=item_data['desc']
                    )
                    db.session.add(item)
                    db.session.flush()
                    total_items += 1
                    print(f"   + {item_data['name']}")
                
                # Buat 2-4 unit per item
                num_units = random.randint(2, 4)
                for i in range(1, num_units + 1):
                    sn = f"{prefix}-{random.randint(100, 999)}"
                    
                    # Pastikan SN unik
                    while Unit.query.filter_by(serial_number=sn).first():
                        sn = f"{prefix}-{random.randint(100, 999)}"
                    
                    status = random.choice(statuses)
                    unit = Unit(
                        item_id=item.id,
                        serial_number=sn,
                        status=status,
                        last_check_in=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                    )
                    db.session.add(unit)
                    db.session.flush()
                    total_units += 1
                    
                    # Buat transaksi jika status Rented/Maintenance
                    if status != 'Ready':
                        trans_type = 'OUT' if status == 'Rented' else 'IN'
                        notes = f"Event: {random.choice(locations)}" if status == 'Rented' else 'Perlu perbaikan/servis'
                        
                        trans = AssetTransaction(
                            unit_id=unit.id,
                            type=trans_type,
                            notes=notes,
                            admin_id=admin.id,
                            timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                        )
                        db.session.add(trans)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print(f"[OK] SELESAI!")
        print(f"   - {total_items} master barang ditambahkan")
        print(f"   - {total_units} unit alat ditambahkan")
        print("="*50)

if __name__ == "__main__":
    seed_pcm_data()
