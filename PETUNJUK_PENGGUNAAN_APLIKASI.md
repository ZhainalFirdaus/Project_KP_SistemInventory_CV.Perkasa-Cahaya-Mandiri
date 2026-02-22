PETUNJUK PENGGUNAAN
APLIKASI INVENTORY MANAGEMENT SYSTEM (FIFO)
CV. PERKASA CAHAYA MANDIRI

Dokumen ini berisi panduan penggunaan Aplikasi Inventory Management yang dirancang untuk mendukung operasional gudang, pengelolaan unit alat (Lighting, Audio, dll), dan pencatatan transaksi keluar-masuk barang menggunakan prinsip FIFO (First-In First-Out).

1. PENDAHULUAN
Aplikasi ini dirancang untuk mempermudah CV. Perkasa Cahaya Mandiri dalam mengelola inventory peralatan produksi secara digital. Sistem ini fokus pada rotasi penggunaan alat yang adil (FIFO), pemantauan kondisi unit (Ready/Maintenance), serta pencatatan riwayat event untuk setiap unit yang disewa.

2. PERSYARATAN SISTEM DAN INSTALASI
A. Persyaratan Sistem
- Python versi 3.11 atau lebih baru.
- Web Browser modern (Google Chrome / Microsoft Edge).
- Koneksi ke database MySQL (Localhost via Laragon/XAMPP).

B. Langkah Instalasi
1. Buka Terminal atau Command Prompt pada direktori utama aplikasi.
2. Pasang dependensi: `pip install -r requirements.txt`.
3. Jalankan aplikasi: `python app.py` atau `python run.py`.
4. Akses melalui browser: `http://127.0.0.1:5000`.

3. LOGIN ADMIN
1. Masukkan Username dan Password administrator.
2. Klik tombol Login. 
   - Jika berhasil, Anda akan diarahkan ke Dashboard.
   - Gunakan fitur Logout untuk mengakhiri sesi keamanan.

4. FITUR UTAMA APLIKASI
A. Dashboard (Ringkasan Statistik)
Menampilkan kondisi gudang secara keseluruhan:
- Total Item: Berbagai kategori alat yang tersedia.
- Total Unit: Jumlah fisik alat secara keseluruhan.
- Status Unit: Grafik/Angka unit yang Ready (Tersedia), Rented (Disewa), dan Maintenance (Servis).
- Aktivitas Terakhir: Log transparan mengenai tindakan admin terbaru.

B. Manajemen Aset (Barang & Unit)
1. Tambah Barang Baru:
   - Pilih menu "Inventory" > "Add Item".
   - Isi Nama Alat, Kategori (Lighting/Audio/dll), dan Jumlah Unit.
   - Sistem akan otomatis menghasilkan Serial Number (SN) unik dengan prefix kategori.
2. Update/Edit Barang:
   - Klik "Edit" pada item untuk mengubah nama, kategori, atau menambah stok unit baru secara massal.
   - Anda juga bisa mengubah status unit secara individu (misal: jika ada unit yang rusak saat di gudang).

C. Transaksi Keluar (Asset Out - FIFO Priority)
Modul ini digunakan saat barang akan keluar untuk sebuah Event/Job.
1. Pilih Item: Pilih jenis alat yang akan dikeluarkan.
2. Seleksi FIFO: Sistem akan menampilkan daftar unit dengan status "Ready" yang diurutkan berdasarkan tanggal masuk terlama (FIFO). Unit terlama berada di baris paling atas.
3. Input Data Event: Masukkan Nama Event (minimal 3 karakter) dan Lokasi Event.
4. Klik Submit: Status unit akan berubah menjadi "Rented" dan histori transaksi dicatat.
5. Surat Jalan: Setelah transaksi, Anda dapat langsung mengunduh/mencetak PDF Surat Jalan.

D. Transaksi Masuk (Asset In - Update Rotasi)
Modul ini digunakan saat barang kembali dari Event.
1. Pilih Item: Pilih jenis alat yang kembali.
2. Pilih Unit: Centang unit-unit yang telah kembali.
3. Cek Kondisi: Pilih kondisi setiap unit (Good/Broken). 
   - Jika "Good", status menjadi "Ready" dan tanggal masuk diperbarui (masuk antrean FIFO terakhir).
   - Jika "Broken", status menjadi "Maintenance" agar tidak bisa disewa sementara waktu.
4. Klik Simpan: Update stok dan antrean FIFO berhasil dilakukan.

E. Laporan & Audit (Reporting)
1. Laporan Inventaris: Rekap seluruh data unit beserta statusnya saat ini (Export Excel/PDF).
2. Laporan Transaksi: Histori riwayat keluar-masuk barang untuk audit penggunaan alat.
3. Activity Logs: Catatan kronologis setiap aksi admin untuk keamanan data.

5. TROUBLESHOOTING (PEMECAHAN MASALAH)
1. Unit Tidak Muncul di Menu "Asset Out"
   - Penyebab: Status unit masih "Rented" (belum dikembalikan) atau "Maintenance" (sedang servis).
   - Solusi: Pastikan unit sudah diproses melalui menu "Asset In" dengan kondisi yang baik.
2. Serial Number Duplikat
   - Penyebab: Mencoba memasukkan unit secara manual dengan SN yang sudah ada.
   - Solusi: Gunakan fitur auto-increment sistem untuk memastikan SN selalu unik.
3. Gagal Cetak PDF (Internal Server Error)
   - Penyebab: Karakter aneh pada Nama Event atau folder `static/uploads` tidak dapat diakses.
   - Solusi: Hindari penggunaan simbol berlebihan pada nama event dan pastikan script memiliki izin menulis file.
