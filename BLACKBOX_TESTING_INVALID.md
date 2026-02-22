PENGUJIAN BLACKBOX TESTING (INVALID SCENARIOS)
APLIKASI INVENTORY MANAGEMENT SYSTEM (FIFO)
CV. PERKASA CAHAYA MANDIRI

Dokumen ini merincikan skenario pengujian negatif (Negative Testing) untuk memastikan sistem memiliki validasi yang kuat terhadap input yang tidak valid, data aneh, atau tindakan yang tidak diizinkan.

| No | Modul / Fitur | Skenario Pengujian (Negative) | Input | Output yang Diharapkan | Status |
|----|---------------|-------------------------------|-------|------------------------|--------|
| 1 | **Login** | Masuk dengan username yang tidak terdaftar | User: `unknown`, Pass: `123` | Sistem menampilkan pesan error "Invalid Credentials" | Berhasil |
| 2 | **Login** | Mengosongkan form login | User: `(kosong)`, Pass: `(kosong)` | Browser/Sistem meminta pengisian field wajib | Berhasil |
| 3 | **Profile Admin** | Mengubah password dengan konfirmasi yang tidak cocok | Pass Baru: `123`, Konfirmasi: `456` | Muncul pesan "Password baru tidak cocok!" | Berhasil |
| 4 | **Tambah Barang** | Mengosongkan nama alat | Nama: `(kosong)`, Qty: `1` | Muncul pesan "Nama alat tidak boleh kosong." | Berhasil |
| 5 | **Tambah Barang** | Input nama alat yang sangat pendek | Nama: `xy`, Qty: `1` | Muncul pesan "Nama alat terlalu pendek (minimal 3 karakter)." | Berhasil |
| 6 | **Tambah Barang** | Input jumlah unit nol atau negatif | Nama: `Moving Head`, Qty: `0` | Muncul pesan "Jumlah unit minimal adalah 1." | Berhasil |
| 7 | **Tambah Barang** | Input data asal/key-mashing (Anti Key-mashing) | Nama: `qwertyuiopasdf` | Sistem mendeteksi pola teks acak dan menampilkan pesan error validasi | Berhasil |
| 8 | **Tambah Barang** | Upload file gambar selain format foto (misal: `.txt`) | File: `catatan.txt` | Sistem menolak file dan (biasanya) menggunakan gambar default atau memunculkan error format | Berhasil |
| 9 | **Asset Out** | Melakukan checkout tanpa memilih unit alat | Pilih Alat, Nama Event: `Job A`, Unit: `(tidak dicentang)` | Muncul pesan "Pilih minimal satu unit untuk dikeluarkan." | Berhasil |
| 10 | **Asset Out** | Mengisikan nama event yang terlalu pendek | Nama Event: `J`, Unit: `SN-01` | Muncul pesan "Nama Event tidak valid (minimal 3 karakter)." | Berhasil |
| 11 | **Asset Out** | Input nama event berupa karakter acak | Nama Event: `fghjklmnbvcxz` | Muncul pesan error deteksi input tidak valid (Anti Key-mashing) | Berhasil |
| 12 | **Asset In** | Memproses kembali tanpa memilih unit yang disewa | Event Asal: `Job A`, Unit: `(tidak dicentang)` | Muncul pesan "Tidak ada unit yang dipilih untuk dikembalikan." | Berhasil |
| 13 | **Asset In** | Mengosongkan data event asal pada pengembalian | Event Asal: `(kosong)` | Muncul pesan "Data Event asal tidak valid." | Berhasil |
| 14 | **Keamanan** | Mengakses halaman admin tanpa login (URL Direct Access) | URL: `/items` atau `/dashboard` | Sistem otomatis mengalihkan (redirect) user ke halaman login | Berhasil |

---

### Kesimpulan Pengujian Negatif
Aplikasi telah dilengkapi dengan mekanisme *Error Handling* dan *Input Validation* yang cukup ketat di sisi server (Flask). Sistem berhasil menolak berbagai variasi input "sampah" atau tindakan ilegal, sehingga integritas data di database tetap terjaga.
