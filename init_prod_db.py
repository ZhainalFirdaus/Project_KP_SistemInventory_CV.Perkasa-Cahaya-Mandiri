from inventory_app import create_app
from inventory_app.extensions import db

app = create_app()
with app.app_context():
    print("Inisialisasi database di server...")
    db.create_all()
    print("Berhasil! Semua tabel telah dibuat di database production.")
