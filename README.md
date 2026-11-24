# PustakaKu — Sistem Informasi Perpustakaan (CRUD)

Aplikasi CRUD Sistem Informasi Perpustakaan berbasis **Python**, **Flask**, dan **SQLite**.

## Teknologi yang Digunakan
- **Bahasa & Framework:** Python + Flask.
- **Database:** SQLite (`perpustakaan.db`) — tidak memerlukan XAMPP / MySQL terpisah.

## Fitur Utama
- **Dashboard:** Ringkasan jumlah judul buku, total stok, anggota aktif, transaksi peminjaman, dan peminjaman terbaru.
- **Data Buku (CRUD + Filter + Export CSV):** Tambah, cari, filter kategori, edit, hapus buku, dan ekspor data ke CSV.
- **Data Anggota (CRUD + Export CSV):** Kelola data anggota, pantau pinjaman aktif & riwayat transaksi, serta ekspor ke CSV.
- **Peminjaman & Pengembalian (Export CSV):** Catat peminjaman, pantau keterlambatan & estimasi denda, proses pengembalian buku dengan update stok otomatis, dan ekspor ke CSV.
- **Laporan & Rekap:** Rekap keterlambatan aktif, estimasi denda berjalan, buku terpopuler, dan peminjam teraktif.
- **Mode Tampilan:** Dukungan Mode Terang dan Mode Gelap.

## Cara Menjalankan
1. Pastikan Python dan Flask sudah terpasang:
   ```bash
   pip install flask
