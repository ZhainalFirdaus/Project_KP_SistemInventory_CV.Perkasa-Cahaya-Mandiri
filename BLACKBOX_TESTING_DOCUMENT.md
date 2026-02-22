PENGUJIAN BLACKBOX TESTING
APLIKASI INVENTORY MANAGEMENT SYSTEM (FIFO)
CV. PERKASA CAHAYA MANDIRI

Dokumen ini merincikan skenario pengujian fungsionalitas aplikasi menggunakan metode Blackbox Testing untuk memastikan seluruh fitur berjalan sesuai dengan logika bisnis yang diharapkan.

### Daftar Fitur Berhasil (Working Features)
- [x] Autentikasi Admin (Hash Password & Session)
- [x] Dashboard Statistik (Visualisasi Data Riil)
- [x] Manajemen Barang & Unit (Auto Serial Number & Image Upload)
- [x] Validasi Anti Key-Mashing (Deteksi input asal-asalan)
- [x] Logika FIFO pada Transaksi Keluar
- [x] Update Rotasi FIFO pada Transaksi Masuk
- [x] Pelaporan PDF & Excel (Cetak Surat Jalan & Inventory)
- [x] Activity Log (Audit Trail Aksi Admin)

---

### Tabel Pengujian Blackbox

| No | Modul / Fitur | Skenario Pengujian | Input | Output yang Diharapkan | Status |
|----|---------------|--------------------|-------|------------------------|--------|
| 1 | **Login** | Masuk ke sistem dengan kredensial yang salah | Username: `salah`, Password: `abc` | Muncul pesan "Invalid Credentials" | Berhasil |
| 2 | **Login** | Masuk ke sistem dengan kredensial yang benar | Username: `admin`, Password: `[password]` | Berhasil login dan dialihkan ke Dashboard | Berhasil |
| 3 | **Tambah Barang** | Input nama barang yang terlalu pendek | Nama: `Ab` | Muncul pesan "Nama alat terlalu pendek (minimal 3 karakter)" | Berhasil |
| 4 | **Tambah Barang** | Input nama barang berupa karakter acak (Key-mashing) | Nama: `asdfghjkl`, Qty: `5` | Muncul pesan peringatan deteksi input tidak valid (Anti Key-mashing) | Berhasil |
| 5 | **Tambah Barang** | Menambah item baru dengan kategori tertentu | Nama: `Mic Wireless`, Kategori: `Audio`, Qty: `2` | Berhasil simpan, SN otomatis menjadi `AUD-MW-1`, `AUD-MW-2` | Berhasil |
| 6 | **Transaksi Keluar** | Memilih unit untuk event tanpa mengisi nama event | Pilih 2 Unit, Nama Event: `(Kosong)` | Muncul pesan "Nama Event tidak valid" | Berhasil |
| 7 | **Transaksi Keluar (FIFO)** | Melakukan transaksi keluar untuk item yang sama berkali-kali | Pilih Item, Klik 'Checkout' | Sistem otomatis mencentang unit dengan `last_check_in` paling lama | Berhasil |
| 8 | **Transaksi Masuk** | Mengembalikan unit yang sedang disewa | Unit SN `LGT-MH-1`, Kondisi: `Good` | Status unit berubah jadi `Ready`, `last_check_in` terupdate ke waktu sekarang | Berhasil |
| 9 | **Transaksi Masuk** | Unit kembali dengan kondisi rusak | Unit SN `LGT-MH-3`, Kondisi: `Broken` | Status unit menjadi `Maintenance`, tidak muncul di daftar unit siap sewa | Berhasil |
| 10 | **Pelaporan** | Mencetak Surat Jalan setelah transaksi keluar | Klik "Download Surat Jalan" | Sistem menghasilkan file PDF dengan detail Event, Lokasi, dan Daftar SN | Berhasil |
| 11 | **Pelaporan** | Ekspor data inventory ke Excel | Klik "Export Excel" di menu Laporan | Mengunduh file `.xlsx` berisi tabel inventory lengkap | Berhasil |
| 12 | **Activity Log** | Memeriksa riwayat tindakan admin | Hapus salah satu unit alat | Aksi "Hapus Barang" muncul di tabel log beserta detail nama alat dan waktu | Berhasil |
| 13 | **Profile Admin** | Mengubah password akun admin | Pass Baru: `admin123`, Confirm: `admin123` | Profil diperbarui, login berikutnya harus menggunakan password baru | Berhasil |

---

### Kesimpulan Pengujian
Berdasarkan hasil pengujian di atas, seluruh fitur utama mulai dari modul Autentikasi hingga Manajemen Transaksi FIFO telah memenuhi kriteria keberhasilan fungsional (100% Pass). Sistem mampu menangani validasi input dasar serta menjalankan logika rotasi barang sesuai dengan kebutuhan CV. Perkasa Cahaya Mandiri.
