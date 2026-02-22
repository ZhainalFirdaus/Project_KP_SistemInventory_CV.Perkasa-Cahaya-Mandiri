from inventory_app import create_app
from inventory_app.extensions import db
import os

def fix_database():
    print("Mengecek dan memperbaiki struktur database...")
    app = create_app()
    with app.app_context():
        try:
            # create_all() hanya akan membuat tabel yang BELUM ada
            db.create_all()
            print("Berhasil! Semua tabel (termasuk activity_log) sudah tersedia.")
        except Exception as e:
            print(f"Gagal memperbarui database: {str(e)}")

if __name__ == "__main__":
    fix_database()
