from inventory_app import create_app
from inventory_app.extensions import db

app = create_app()
with app.app_context():
    print("="*50)
    print("Mengecek koneksi database...")
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        print("✓ Koneksi database berhasil!")
        
        print("Inisialisasi tabel-tabel...")
        db.create_all()
        print("✓ Semua tabel telah dibuat atau sudah ada.")
    except Exception as e:
        print(f"✗ ERROR DATABASE: {str(e)}")
        print("Pastikan DATABASE_URL di Railway Variables sudah benar.")
    print("="*50)
