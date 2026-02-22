LAMPIRAN C
DOKUMEN TEKNIK
PROFIL LENGKAP APLIKASI
INVENTORY MANAGEMENT SYSTEM (FIFO)

1. Deskripsi Umum
Inventory Management System (FIFO) adalah aplikasi berbasis web yang dirancang khusus untuk mengelola inventory peralatan produksi, memantau kondisi unit alat, serta mencatat transaksi keluar-masuk barang di CV. Perkasa Cahaya Mandiri. Aplikasi ini bertujuan untuk mendigitalkan proses manajemen aset yang sebelumnya manual, memastikan rotasi alat yang adil menggunakan logika First-In First-Out (FIFO), serta mempermudah pemantauan status alat secara real-time.

Tujuan Utama:
a. Meningkatkan akurasi data stok dan unit alat (Lighting, Audio, Multimedia, dll).
b. Mengoptimalkan rotasi penggunaan alat dengan prinsip FIFO (First-In First-Out).
c. Mempermudah pelacakan status unit (Tersedia, Disewa, atau Servis).
d. Menyediakan laporan inventory dan histori transaksi yang terstruktur dan siap cetak.

2. Fitur Utama
Aplikasi ini dilengkapi dengan modul fungsional yang terintegrasi untuk mendukung operasional gudang:

A. Dashboard
Menyajikan ringkasan statistik secara real-time, termasuk total item barang, total unit alat, jumlah unit yang tersedia, sedang disewa, atau dalam perbaikan, serta grafik aktivitas terbaru.

B. Manajemen Data Master (Inventory)
- Data Barang: Pengelolaan kategori produk utama (seperti Lighting, Multimedia, dll) beserta deskripsi dan gambar.
- Data Unit Alat: Pengelolaan unit individu dengan Serial Number unik, kondisi, dan riwayat check-in.
- QR Code: Setiap unit alat dapat diidentifikasi secara unik melalui QR Code untuk kemudahan akses data (Opsional).

C. Manajemen Transaksi (FIFO Logic)
- Asset Out (Keluar): Pencatatan unit yang keluar untuk disewa atau dipinjam. Sistem secara otomatis memprioritaskan unit yang paling lama "menganggur" di gudang (berdasarkan tanggal check-in terakhir).
- Asset In (Kembali): Pencatatan unit yang kembali ke gudang. Status unit akan kembali menjadi "Tersedia" dan tanggal check-in diperbarui ke waktu sekarang agar masuk antrean FIFO terakhir.
- Status Management: Pemantauan status unit yang berubah otomatis antara Ready, Rented, dan Maintenance.

D. Log Aktivitas & Keamanan
- Activity Log: Mencatat setiap tindakan yang dilakukan administrator (tambah barang, hapus unit, login) untuk tujuan audit trail.
- Autentikasi: Sistem login administrator yang aman menggunakan enkripsi password (hashing).

E. Pelaporan (Reporting)
- Laporan Inventaris: Rekap daftar barang dan unit dalam format PDF atau Excel.
- Laporan Transaksi: Histori transaksi keluar-masuk barang untuk periode tertentu yang siap cetak.

3. Arsitektur Teknis
Aplikasi dibangun menggunakan stack teknologi modern untuk memastikan performa yang ringan dan kemudahan pemeliharaan.

Tech Stack yang Digunakan:
- Bahasa Pemrograman: Python 3.11, HTML5, CSS3 (Tailwind CSS), JavaScript
- Framework: Flask (Web Framework)
- Database: MySQL (Localhost via Laragon/XAMPP)
- ORM (Object Relational Mapping): SQLAlchemy

Library Utama:
- Flask-SQLAlchemy: Integrasi basis data relasional.
- Flask-Login: Manajemen sesi pengguna dan proteksi rute.
- mysql-connector-python: Driver koneksi database MySQL.
- ReportLab & Pandas: Pembuatan dokumen laporan PDF dan ekspor data Excel.
- Werkzeug: Keamanan hashing password.
- QRCODE: Pembuatan kode QR untuk unit alat.

Struktur Proyek Aplikasi (MVC):
- inventory_app
    - routes: Logika navigasi dan pengolahan data (auth, items, transactions, reports, dll).
    - models.py: Definisi skema database (User, Item, Unit, AssetTransaction, ActivityLog).
    - utils: Fungsi bantuan (validasi, format tanggal, pemrosesan file).
    - templates: Antarmuka UI menggunakan Jinja2 dan Tailwind CSS.
    - static: Aset gambar, CSS, dan JavaScript.
- config.py / .env: Konfigurasi sistem dan kredensial database.
- run.py / app.py: Entry point aplikasi.
- requirements.txt: Daftar dependensi Python.

4. Struktur Data (Model Database)
Tabel utama dalam basis data:

Nama Tabel      | Deskripsi
----------------|---------------------------------------------------------------
users           | Data administrator (username, password hash, profile img).
item            | Kategori produk (nama, kategori, deskripsi).
unit            | Unit fisik individu (serial number, status, last_check_in).
asset_transaction| Riwayat transaksi keluar (OUT) dan masuk (IN).
activity_log    | Catatan aktivitas admin untuk transparansi sistem.

5. Panduan Instalasi dan Pengoperasian
Prasyarat Sistem:
- Python versi 3.11 atau lebih tinggi.
- Laragon/XAMPP (untuk database MySQL).

Langkah Instalasi:
1. Pastikan server MySQL berjalan dan buat database: `inventory_kp`.
2. Buka terminal di direktori proyek.
3. Instal dependensi: `pip install -r requirements.txt`.
4. Sesuaikan konfigurasi database pada file `.env`.
5. Inisialisasi database (jika diperlukan): `python create_db.py`.
6. Jalankan aplikasi: `python app.py` (atau `flask run`).
7. Akses melalui browser: `http://127.0.0.1:5000`.

6. Penutup
Dokumen ini disusun sebagai profil teknis untuk aplikasi Inventory Management System (FIFO) CV. Perkasa Cahaya Mandiri. Dokumentasi ini menjadi acuan teknis standar bagi pemeliharaan dan pengembangan sistem di masa mendatang.
