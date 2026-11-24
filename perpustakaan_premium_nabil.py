from flask import Flask, request, redirect, url_for, flash, render_template_string, Response
import sqlite3
import csv
import io
import re
from pathlib import Path
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = "pustakaku-enterprise-key-2026"
DB_PATH = Path(__file__).with_name("perpustakaan.db")

DENDA_PER_HARI = 2000
MAX_PINJAM_AKTIF = 3

# =========================
# DATABASE & INISIALISASI
# =========================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS anggota (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode TEXT NOT NULL UNIQUE,
            nama TEXT NOT NULL,
            alamat TEXT,
            tgl_daftar TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS buku (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode TEXT NOT NULL UNIQUE,
            judul TEXT NOT NULL,
            penulis TEXT NOT NULL,
            kategori TEXT NOT NULL,
            tahun INTEGER,
            stok INTEGER NOT NULL DEFAULT 0 CHECK (stok >= 0)
        );

        CREATE TABLE IF NOT EXISTS peminjaman (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anggota_id INTEGER,
            nama_peminjam TEXT NOT NULL,
            buku_id INTEGER NOT NULL,
            tanggal_pinjam TEXT NOT NULL,
            tanggal_kembali TEXT NOT NULL,
            tanggal_dikembalikan TEXT,
            status TEXT NOT NULL DEFAULT 'Dipinjam',
            FOREIGN KEY (anggota_id) REFERENCES anggota(id),
            FOREIGN KEY (buku_id) REFERENCES buku(id)
        );
        """)

        cols_p = [r["name"] for r in db.execute("PRAGMA table_info(peminjaman)").fetchall()]
        if "anggota_id" not in cols_p:
            db.execute("ALTER TABLE peminjaman ADD COLUMN anggota_id INTEGER")
        if "tanggal_dikembalikan" not in cols_p:
            db.execute("ALTER TABLE peminjaman ADD COLUMN tanggal_dikembalikan TEXT")

        if db.execute("SELECT COUNT(*) FROM anggota").fetchone()[0] == 0:
            db.executemany("""
                INSERT INTO anggota (kode, nama, alamat, tgl_daftar)
                VALUES (?, ?, ?, ?)
            """, [
                ("AGT01", "Andi Pratama", "Jl. Ketintang Baru I No. 12, Surabaya", "2026-08-10"),
                ("AGT02", "Nadia Putri", "Jl. Ahmad Yani No. 45, Waru, Sidoarjo", "2026-08-18"),
                ("AGT03", "Rizky Maulana", "Jl. Karah Agung No. 8, Surabaya", "2026-09-02"),
                ("AGT04", "Dewi Lestari", "Jl. Jemursari Selatan No. 19, Surabaya", "2026-09-15"),
            ])

        if db.execute("SELECT COUNT(*) FROM buku").fetchone()[0] == 0:
            db.executemany("""
                INSERT INTO buku (kode, judul, penulis, kategori, tahun, stok)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                ("BK001", "Laskar Pelangi", "Andrea Hirata", "Novel", 2005, 8),
                ("BK002", "Bumi", "Tere Liye", "Fiksi", 2014, 6),
                ("BK003", "Atomic Habits", "James Clear", "Pengembangan Diri", 2018, 5),
                ("BK004", "Dasar-Dasar Pemrograman Python", "Abdul Kadir", "Teknologi", 2021, 4),
                ("BK005", "Negeri 5 Menara", "Ahmad Fuadi", "Novel", 2009, 7),
            ])

def hitung_hari_terlambat(tgl_batas_str, status):
    if status != "Dipinjam" or not tgl_batas_str:
        return 0
    try:
        batas = date.fromisoformat(tgl_batas_str)
        selisih = (date.today() - batas).days
        return selisih if selisih > 0 else 0
    except ValueError:
        return 0

def hitung_denda(hari_telat):
    return max(0, int(hari_telat)) * DENDA_PER_HARI

def format_rupiah(nominal):
    return f"Rp {int(nominal):,}".replace(",", ".")

def csv_response(filename, headers, rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    return Response(
        buf.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# =========================
# TEMPLATE HTML + CSS
# =========================
PAGE = r"""
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }} | PustakaKu</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --navy:#14213d;--blue:#3157d5;--light:#f4f7fc;--card:#ffffff;--text:#202a3c;
  --muted:#778198;--line:#e8edf5;--row-line:#f0f2f7;--soft-btn:#eef2ff;--sub:#8993a5;
  --green:#169b72;--red:#d94c5c;--orange:#d98218
}
body.dark{
  --navy:#0b1222;--blue:#4c73f0;--light:#0f172a;--card:#17223b;--text:#e2e8f0;
  --muted:#94a3b8;--line:#26344f;--row-line:#202d46;--soft-btn:#223254;--sub:#94a3b8
}
*{box-sizing:border-box}body{margin:0;background:var(--light);font-family:'DM Sans',sans-serif;color:var(--text);transition:background .2s,color .2s}
.layout{display:flex;min-height:100vh}.sidebar{width:245px;background:var(--navy);color:white;padding:27px 18px;position:fixed;inset:0 auto 0 0;z-index:20}
.brand{display:flex;align-items:center;gap:12px;padding:0 10px 28px}.brand-icon{width:42px;height:42px;border-radius:13px;background:#4268e8;display:grid;place-items:center;font-size:22px}.brand strong{font:800 19px 'Plus Jakarta Sans'}.brand small{display:block;color:#aebbd7;font-size:11px;margin-top:3px}
.nav-label{font-size:10px;letter-spacing:1.5px;color:#8d9bb8;padding:10px 12px}.nav a{display:flex;align-items:center;gap:12px;color:#c7d0e3;text-decoration:none;padding:11px 12px;border-radius:10px;margin:4px 0;font-size:14px}.nav a.active,.nav a:hover{background:#293c68;color:white}.nav .ico{width:20px;text-align:center}
.main{margin-left:245px;width:calc(100% - 245px);padding:30px 38px 50px}.topbar{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:28px;flex-wrap:wrap}.eyebrow{font-size:12px;color:var(--muted);margin-bottom:5px}.topbar h1{font:800 25px 'Plus Jakarta Sans';margin:0;color:var(--text)}.top-right{display:flex;align-items:center;gap:10px}
.profile{background:var(--card);border:1px solid var(--line);border-radius:30px;padding:9px 15px;font-size:12px;color:var(--muted)}
.theme-btn{background:var(--card);border:1px solid var(--line);border-radius:30px;padding:9px 14px;font:600 12px 'DM Sans';color:var(--text);cursor:pointer}
.welcome{background:linear-gradient(115deg,#263f91,#4269e8);border-radius:18px;padding:25px 28px;color:white;margin-bottom:22px;position:relative;overflow:hidden}.welcome:after{content:"📚";position:absolute;right:35px;top:15px;font-size:70px;opacity:.18}.welcome h2{font:700 20px 'Plus Jakarta Sans';margin:0 0 8px}.welcome p{margin:0;color:#dce5ff;font-size:13px;max-width:560px;line-height:1.6}.quick-row{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:22px}.stat,.panel{background:var(--card);border:1px solid var(--line);border-radius:15px;padding:20px}.stat-top{display:flex;justify-content:space-between;color:var(--muted);font-size:12px}.stat-icon{width:34px;height:34px;border-radius:10px;background:var(--soft-btn);display:grid;place-items:center}.stat strong{display:block;font:800 26px 'Plus Jakarta Sans';margin-top:12px;color:var(--text)}.stat small{color:var(--muted);font-size:11px}
.panel{padding:21px;margin-bottom:18px}.panel-head{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:17px;flex-wrap:wrap}.panel-actions{display:flex;gap:8px;flex-wrap:wrap}.panel h3{font:700 16px 'Plus Jakarta Sans';margin:0;color:var(--text)}.muted{color:var(--muted);font-size:12px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:10px 14px;border:0;border-radius:9px;background:var(--blue);color:white;text-decoration:none;font:600 12px 'DM Sans';cursor:pointer}.btn:hover{filter:brightness(.95)}.btn-light{background:var(--soft-btn);color:var(--blue)}.btn-danger{background:rgba(217,76,92,.14);color:#ef5366}.btn-success{background:rgba(22,155,114,.15);color:#20b889}.btn-white{background:white;color:#14213d}
.toolbar{display:flex;gap:10px;align-items:center;margin-bottom:15px;flex-wrap:wrap}.search,.filter-select{border:1px solid var(--line);border-radius:9px;padding:10px 12px;font:13px 'DM Sans';background:var(--card);color:var(--text)}.search{flex:1;min-width:220px;max-width:360px;outline:none}.search:focus,input:focus,select:focus{border-color:#8ca3f5!important;outline:none}
table{width:100%;border-collapse:collapse;font-size:12px}th{text-align:left;color:var(--muted);font-weight:600;padding:12px 10px;border-bottom:1px solid var(--line);white-space:nowrap}td{padding:13px 10px;border-bottom:1px solid var(--row-line);vertical-align:middle}tr:last-child td{border-bottom:0}.book-title{font-weight:700;color:var(--text)}.sub{display:block;color:var(--sub);font-size:11px;margin-top:4px}
.pill{display:inline-block;padding:5px 9px;border-radius:20px;font-size:10px;font-weight:700;background:var(--soft-btn);color:var(--blue)}.pill.green{background:rgba(22,155,114,.15);color:#20b889}.pill.orange{background:rgba(217,130,24,.16);color:#e08e26}.pill.red{background:rgba(217,76,92,.16);color:#ef5366}
.actions{display:flex;gap:6px;flex-wrap:wrap}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}.field{display:flex;flex-direction:column;gap:7px}.field.full{grid-column:1/-1}.field label{font-size:12px;font-weight:700;color:var(--text)}.field input,.field select{padding:11px 12px;border:1px solid var(--line);border-radius:9px;font:13px 'DM Sans';background:var(--card);color:var(--text)}.form-actions{display:flex;gap:9px;margin-top:20px;flex-wrap:wrap}
.flash{padding:12px 15px;border-radius:10px;background:rgba(22,155,114,.15);color:#20b889;font-size:13px;margin-bottom:15px;border:1px solid rgba(22,155,114,.3)}
.flash.danger{background:rgba(217,76,92,.15);color:#ef5366;border-color:rgba(217,76,92,.3)}
.flash.warning{background:rgba(217,130,24,.15);color:#e08e26;border-color:rgba(217,130,24,.3)}
.empty{text-align:center;color:var(--muted);padding:30px}
.info-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.info-box{background:var(--light);border:1px solid var(--line);border-radius:12px;padding:15px}.info-box h4{margin:0 0 8px;font:700 14px 'Plus Jakarta Sans';color:var(--text)}.info-box ul{margin:0;padding-left:18px;font-size:12.5px;color:var(--muted);line-height:1.7}
.footer{text-align:center;color:var(--muted);font-size:11px;margin-top:28px}
@media(max-width:1100px){.stats{grid-template-columns:repeat(2,1fr)}}
@media(max-width:850px){.sidebar{width:68px;padding:20px 9px}.brand{padding:0 3px 30px}.brand strong,.brand small,.nav-label,.nav a span:not(.ico){display:none}.nav a{justify-content:center;padding:13px}.main{margin-left:68px;width:calc(100% - 68px);padding:22px 16px}.welcome:after{right:15px}.table-wrap{overflow-x:auto}.info-grid{grid-template-columns:1fr}}
@media(max-width:520px){.topbar{align-items:flex-start}.topbar h1{font-size:21px}.profile{display:none}.form-grid,.stats{grid-template-columns:1fr}.field.full{grid-column:auto}.panel{padding:15px}.toolbar{flex-wrap:wrap}.search{max-width:none;width:100%}}
</style>
</head>
<body>
<script>
if(localStorage.getItem("pustakaku_theme")==="dark"){document.body.classList.add("dark");}
</script>
<div class="layout">
<aside class="sidebar">
 <div class="brand"><div class="brand-icon">📚</div><div><strong>PustakaKu</strong><small>Library Management</small></div></div>
 <div class="nav-label">MENU UTAMA</div>
 <nav class="nav">
  <a href="{{ url_for('dashboard') }}" class="{{ 'active' if active=='dashboard' else '' }}"><span class="ico">▦</span><span>Dashboard</span></a>
  <a href="{{ url_for('books') }}" class="{{ 'active' if active=='books' else '' }}"><span class="ico">▤</span><span>Data Buku</span></a>
  <a href="{{ url_for('members') }}" class="{{ 'active' if active=='members' else '' }}"><span class="ico">👤</span><span>Data Anggota</span></a>
  <a href="{{ url_for('loans') }}" class="{{ 'active' if active=='loans' else '' }}"><span class="ico">⇄</span><span>Peminjaman</span></a>
  <a href="{{ url_for('reports') }}" class="{{ 'active' if active=='reports' else '' }}"><span class="ico">📊</span><span>Laporan</span></a>
 </nav>
 <div class="nav-label" style="margin-top:24px">INFORMASI</div>
 <nav class="nav"><a href="{{ url_for('about') }}" class="{{ 'active' if active=='about' else '' }}"><span class="ico">ⓘ</span><span>Tentang Sistem</span></a></nav>
</aside>
<main class="main">
 <header class="topbar">
  <div><div class="eyebrow">Sistem Informasi Perpustakaan</div><h1>{{ title }}</h1></div>
  <div class="top-right">
   <button type="button" class="theme-btn" id="themeToggle">🌓 Mode Gelap</button>
   <div class="profile">● Administrator</div>
  </div>
 </header>
 {% with messages = get_flashed_messages(with_categories=true) %}{% if messages %}{% for category, message in messages %}<div class="flash {{ category }}">{{ '✓' if category=='success' else '!' }} {{ message }}</div>{% endfor %}{% endif %}{% endwith %}
 {{ content|safe }}
 <div class="footer">© 2026 PustakaKu · Sistem Informasi Perpustakaan (Flask + SQLite)</div>
</main>
</div>
<script>
document.querySelectorAll('[data-confirm]').forEach(el=>el.addEventListener('click',e=>{if(!confirm(el.dataset.confirm))e.preventDefault()}));
const themeBtn=document.getElementById("themeToggle");
function syncThemeLabel(){
  if(!themeBtn)return;
  themeBtn.textContent=document.body.classList.contains("dark")?"☀️ Mode Terang":"🌙 Mode Gelap";
}
syncThemeLabel();
if(themeBtn){
  themeBtn.addEventListener("click",()=>{
    document.body.classList.toggle("dark");
    localStorage.setItem("pustakaku_theme",document.body.classList.contains("dark")?"dark":"light");
    syncThemeLabel();
  });
}
</script>
</body></html>
"""

def page(title, active, content, **context):
    return render_template_string(PAGE, title=title, active=active, content=content, **context)

# =========================
# DASHBOARD
# =========================
@app.route("/")
def dashboard():
    with get_db() as db:
        total_buku = db.execute("SELECT COUNT(*) FROM buku").fetchone()[0]
        total_stok = db.execute("SELECT COALESCE(SUM(stok),0) FROM buku").fetchone()[0]
        total_anggota = db.execute("SELECT COUNT(*) FROM anggota").fetchone()[0]
        dipinjam_rows = db.execute("SELECT tanggal_kembali, status FROM peminjaman WHERE status='Dipinjam'").fetchall()
        dipinjam = len(dipinjam_rows)
        terlambat = sum(1 for r in dipinjam_rows if hitung_hari_terlambat(r["tanggal_kembali"], r["status"]) > 0)
        recent = db.execute("""
            SELECT p.*, b.judul, b.kode
            FROM peminjaman p
            JOIN buku b ON b.id = p.buku_id
            ORDER BY p.id DESC LIMIT 5
        """).fetchall()

    recent_enriched = []
    for r in recent:
        d = dict(r)
        d["hari_telat"] = hitung_hari_terlambat(r["tanggal_kembali"], r["status"])
        recent_enriched.append(d)

    content = """
    <section class="welcome">
      <h2>Selamat Datang di PustakaKu 👋</h2>
      <p>Kelola koleksi buku, data anggota, transaksi peminjaman, serta rekap laporan perpustakaan dengan validasi data dan pencatatan stok otomatis.</p>
      <div class="quick-row">
        <a class="btn btn-white" href="{{ url_for('book_new') }}">＋ Tambah Buku</a>
        <a class="btn btn-white" href="{{ url_for('member_new') }}">＋ Tambah Anggota</a>
        <a class="btn btn-white" href="{{ url_for('loan_new') }}">⇄ Catat Peminjaman</a>
        <a class="btn btn-white" href="{{ url_for('reports') }}">📊 Lihat Laporan</a>
      </div>
    </section>
    <section class="stats">
      <div class="stat"><div class="stat-top"><span>Judul Buku</span><span class="stat-icon">📚</span></div><strong>{{ total_buku }}</strong><small>Jenis koleksi terdaftar</small></div>
      <div class="stat"><div class="stat-top"><span>Total Stok Buku</span><span class="stat-icon">▤</span></div><strong>{{ total_stok }}</strong><small>Eksemplar siap dipinjam</small></div>
      <div class="stat"><div class="stat-top"><span>Anggota Aktif</span><span class="stat-icon">👤</span></div><strong>{{ total_anggota }}</strong><small>Anggota perpustakaan</small></div>
      <div class="stat"><div class="stat-top"><span>Sedang Dipinjam</span><span class="stat-icon">⇄</span></div><strong>{{ dipinjam }}</strong><small>{{ terlambat }} transaksi terlambat</small></div>
    </section>
    <section class="panel">
      <div class="panel-head"><div><h3>Peminjaman Terbaru</h3><div class="muted">5 transaksi peminjaman terakhir</div></div><a class="btn btn-light" href="{{ url_for('loans') }}">Lihat Semua →</a></div>
      <div class="table-wrap"><table><thead><tr><th>PEMINJAM</th><th>JUDUL BUKU</th><th>TANGGAL PINJAM</th><th>BATAS KEMBALI</th><th>STATUS</th></tr></thead><tbody>
      {% for p in recent %}
      <tr>
        <td><b>{{ p.nama_peminjam }}</b></td>
        <td>{{ p.judul }}<span class="sub">{{ p.kode }}</span></td>
        <td>{{ p.tanggal_pinjam }}</td>
        <td>{{ p.tanggal_kembali }}</td>
        <td>
          {% if p.status == 'Dikembalikan' %}
            <span class="pill green">Dikembalikan</span>
          {% elif p.hari_telat > 0 %}
            <span class="pill red">Terlambat {{ p.hari_telat }} hari</span>
          {% else %}
            <span class="pill orange">Dipinjam</span>
          {% endif %}
        </td>
      </tr>
      {% else %}
      <tr><td colspan="5" class="empty">Belum ada transaksi peminjaman.</td></tr>
      {% endfor %}
      </tbody></table></div>
    </section>
    """
    return page("Dashboard", "dashboard", render_template_string(
        content, total_buku=total_buku, total_stok=total_stok,
        total_anggota=total_anggota, dipinjam=dipinjam, terlambat=terlambat, recent=recent_enriched
    ))

# =========================
# DATA BUKU: READ + CREATE + UPDATE + DELETE + EXPORT
# =========================
@app.route("/buku")
def books():
    q = request.args.get("q", "").strip()
    kategori = request.args.get("kategori", "").strip()
    with get_db() as db:
        categories = [r[0] for r in db.execute("SELECT DISTINCT kategori FROM buku ORDER BY kategori").fetchall()]
        sql = """
            SELECT b.*, COUNT(p.id) AS total_dipinjam
            FROM buku b
            LEFT JOIN peminjaman p ON p.buku_id = b.id
            WHERE 1=1
        """
        params = []
        if q:
            sql += " AND (b.judul LIKE ? OR b.penulis LIKE ? OR b.kode LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
        if kategori:
            sql += " AND b.kategori = ?"
            params.append(kategori)
        sql += " GROUP BY b.id ORDER BY b.kode ASC"
        rows = db.execute(sql, params).fetchall()

    content = """
    <section class="panel">
      <div class="panel-head">
        <div><h3>Daftar Koleksi Buku</h3><div class="muted">Tambah, cari, filter, ubah, hapus, dan ekspor data buku</div></div>
        <div class="panel-actions">
          <a class="btn btn-light" href="{{ url_for('export_books') }}">⬇ Export CSV</a>
          <a class="btn" href="{{ url_for('book_new') }}">＋ Tambah Buku</a>
        </div>
      </div>
      <form class="toolbar" method="get">
        <input class="search" name="q" value="{{ q }}" placeholder="Cari judul, penulis, atau kode buku...">
        <select class="filter-select" name="kategori" onchange="this.form.submit()">
          <option value="">Semua Kategori</option>
          {% for cat in categories %}<option value="{{ cat }}" {{ 'selected' if kategori==cat else '' }}>{{ cat }}</option>{% endfor %}
        </select>
        <button class="btn btn-light">Cari</button>
        {% if q or kategori %}<a class="btn btn-light" href="{{ url_for('books') }}">Reset</a>{% endif %}
      </form>
      <div class="table-wrap"><table><thead><tr><th>KODE</th><th>INFORMASI BUKU</th><th>KATEGORI</th><th>TAHUN</th><th>STOK</th><th>RIWAYAT</th><th>AKSI</th></tr></thead><tbody>
      {% for b in rows %}
      <tr>
        <td><span class="pill">{{ b.kode }}</span></td>
        <td><span class="book-title">{{ b.judul }}</span><span class="sub">{{ b.penulis }}</span></td>
        <td>{{ b.kategori }}</td>
        <td>{{ b.tahun or '-' }}</td>
        <td><span class="pill {{ 'green' if b.stok > 0 else 'red' }}">{{ b.stok }}</span></td>
        <td>{{ b.total_dipinjam }}x</td>
        <td>
          <div class="actions">
            <a class="btn btn-light" href="{{ url_for('book_edit', book_id=b.id) }}">Edit</a>
            <form method="post" action="{{ url_for('book_delete', book_id=b.id) }}">
              <button class="btn btn-danger" data-confirm="Yakin ingin menghapus buku '{{ b.judul }}'?">Hapus</button>
            </form>
          </div>
        </td>
      </tr>
      {% else %}
      <tr><td colspan="7" class="empty">Data buku tidak ditemukan.</td></tr>
      {% endfor %}
      </tbody></table></div>
    </section>
    """
    return page("Data Buku", "books", render_template_string(content, rows=rows, q=q, kategori=kategori, categories=categories))

@app.route("/buku/export.csv")
def export_books():
    with get_db() as db:
        rows = db.execute("SELECT kode, judul, penulis, kategori, tahun, stok FROM buku ORDER BY kode ASC").fetchall()
    return csv_response(
        "data_buku_pustakaku.csv",
        ["Kode", "Judul", "Penulis", "Kategori", "Tahun Terbit", "Stok"],
        [[r["kode"], r["judul"], r["penulis"], r["kategori"], r["tahun"] or "", r["stok"]] for r in rows]
    )

BOOK_FORM = """
<section class="panel"><div class="panel-head"><div><h3>{{ heading }}</h3><div class="muted">Format kode buku disarankan BKxxx (contoh: BK006)</div></div></div>
<form method="post"><div class="form-grid">
<div class="field"><label>Kode Buku</label><input name="kode" required maxlength="10" {{ 'readonly' if mode=='edit' else '' }} value="{{ book.kode if book else '' }}" placeholder="Contoh: BK006"></div>
<div class="field"><label>Judul Buku</label><input name="judul" required maxlength="120" value="{{ book.judul if book else '' }}" placeholder="Masukkan judul buku"></div>
<div class="field"><label>Penulis</label><input name="penulis" required maxlength="80" value="{{ book.penulis if book else '' }}" placeholder="Nama penulis"></div>
<div class="field"><label>Kategori</label><input name="kategori" required maxlength="50" value="{{ book.kategori if book else '' }}" placeholder="Contoh: Teknologi"></div>
<div class="field"><label>Tahun Terbit</label><input type="number" name="tahun" min="1000" max="{{ current_year }}" value="{{ book.tahun if book and book.tahun else '' }}" placeholder="{{ current_year }}"></div>
<div class="field"><label>Stok Buku</label><input type="number" name="stok" min="0" required value="{{ book.stok if book else 0 }}"></div>
</div><div class="form-actions"><button class="btn">Simpan Data</button><a class="btn btn-light" href="{{ url_for('books') }}">Batal</a></div></form></section>
"""

def validasi_buku_input(kode, judul, penulis, kategori, tahun_str, stok_str):
    if not re.fullmatch(r"[A-Za-z]{2,4}\d{2,4}", kode):
        return "Kode buku harus berformat huruf + angka, contoh BK006."
    if not judul or not penulis or not kategori:
        return "Kode, judul, penulis, dan kategori wajib diisi."
    tahun_val = None
    if tahun_str:
        if not tahun_str.isdigit() or int(tahun_str) < 1000 or int(tahun_str) > date.today().year:
            return f"Tahun terbit harus berupa angka antara 1000 dan {date.today().year}."
        tahun_val = int(tahun_str)
    if not stok_str.isdigit() or int(stok_str) < 0:
        return "Stok buku harus bilangan bulat >= 0."
    return None, (kode.upper(), judul, penulis, kategori, tahun_val, int(stok_str))

@app.route("/buku/tambah", methods=["GET", "POST"])
def book_new():
    if request.method == "POST":
        kode = request.form.get("kode", "").strip().upper()
        judul = request.form.get("judul", "").strip()
        penulis = request.form.get("penulis", "").strip()
        kategori = request.form.get("kategori", "").strip()
        tahun_str = request.form.get("tahun", "").strip()
        stok_str = request.form.get("stok", "0").strip()

        res = validasi_buku_input(kode, judul, penulis, kategori, tahun_str, stok_str)
        if isinstance(res, str):
            flash(res, "danger")
        else:
            _, payload = res
            try:
                with get_db() as db:
                    db.execute(
                        "INSERT INTO buku (kode,judul,penulis,kategori,tahun,stok) VALUES (?,?,?,?,?,?)",
                        payload
                    )
                flash("Buku berhasil ditambahkan.", "success")
                return redirect(url_for("books"))
            except sqlite3.IntegrityError:
                flash("Kode buku sudah digunakan.", "danger")

    return page("Tambah Buku", "books", render_template_string(
        BOOK_FORM, heading="Tambah Buku Baru", book=None, mode="tambah", current_year=date.today().year
    ))

@app.route("/buku/edit/<int:book_id>", methods=["GET", "POST"])
def book_edit(book_id):
    with get_db() as db:
        book = db.execute("SELECT * FROM buku WHERE id=?", (book_id,)).fetchone()
        if not book:
            flash("Data buku tidak ditemukan.", "warning")
            return redirect(url_for("books"))

        if request.method == "POST":
            kode = book["kode"]
            judul = request.form.get("judul", "").strip()
            penulis = request.form.get("penulis", "").strip()
            kategori = request.form.get("kategori", "").strip()
            tahun_str = request.form.get("tahun", "").strip()
            stok_str = request.form.get("stok", "0").strip()

            res = validasi_buku_input(kode, judul, penulis, kategori, tahun_str, stok_str)
            if isinstance(res, str):
                flash(res, "danger")
            else:
                _, payload = res
                _, j_val, p_val, k_val, t_val, s_val = payload
                db.execute(
                    "UPDATE buku SET judul=?, penulis=?, kategori=?, tahun=?, stok=? WHERE id=?",
                    (j_val, p_val, k_val, t_val, s_val, book_id)
                )
                flash("Data buku berhasil diperbarui.", "success")
                return redirect(url_for("books"))

    return page("Edit Buku", "books", render_template_string(
        BOOK_FORM, heading="Edit Data Buku", book=book, mode="edit", current_year=date.today().year
    ))

@app.route("/buku/hapus/<int:book_id>", methods=["POST"])
def book_delete(book_id):
    with get_db() as db:
        used = db.execute("SELECT COUNT(*) FROM peminjaman WHERE buku_id=?", (book_id,)).fetchone()[0]
        if used:
            flash("Buku tidak dapat dihapus karena sudah memiliki riwayat peminjaman.", "danger")
        else:
            db.execute("DELETE FROM buku WHERE id=?", (book_id,))
            flash("Data buku berhasil dihapus.", "success")
    return redirect(url_for("books"))

# =========================
# DATA ANGGOTA: CRUD LENGKAP + EXPORT
# =========================
@app.route("/anggota")
def members():
    q = request.args.get("q", "").strip()
    with get_db() as db:
        if q:
            rows = db.execute("""
                SELECT a.*,
                       COUNT(p.id) AS jumlah_pinjam,
                       SUM(CASE WHEN p.status='Dipinjam' THEN 1 ELSE 0 END) AS pinjam_aktif
                FROM anggota a
                LEFT JOIN peminjaman p ON p.anggota_id = a.id OR p.nama_peminjam = a.nama
                WHERE a.kode LIKE ? OR a.nama LIKE ? OR a.alamat LIKE ?
                GROUP BY a.id
                ORDER BY a.kode ASC
            """, (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
        else:
            rows = db.execute("""
                SELECT a.*,
                       COUNT(p.id) AS jumlah_pinjam,
                       SUM(CASE WHEN p.status='Dipinjam' THEN 1 ELSE 0 END) AS pinjam_aktif
                FROM anggota a
                LEFT JOIN peminjaman p ON p.anggota_id = a.id OR p.nama_peminjam = a.nama
                GROUP BY a.id
                ORDER BY a.kode ASC
            """).fetchall()

    content = """
    <section class="panel">
      <div class="panel-head">
        <div><h3>Data Anggota Perpustakaan</h3><div class="muted">Kelola data anggota terdaftar dan pantau status pinjaman</div></div>
        <div class="panel-actions">
          <a class="btn btn-light" href="{{ url_for('export_members') }}">⬇ Export CSV</a>
          <a class="btn" href="{{ url_for('member_new') }}">＋ Tambah Anggota</a>
        </div>
      </div>
      <form class="toolbar" method="get">
        <input class="search" name="q" value="{{ q }}" placeholder="Cari kode, nama, atau alamat anggota...">
        <button class="btn btn-light">Cari</button>
        {% if q %}<a class="btn btn-light" href="{{ url_for('members') }}">Reset</a>{% endif %}
      </form>
      <div class="table-wrap"><table><thead><tr><th>KODE</th><th>NAMA ANGGOTA</th><th>ALAMAT</th><th>TGL DAFTAR</th><th>PINJAM AKTIF</th><th>TOTAL RIWAYAT</th><th>AKSI</th></tr></thead><tbody>
      {% for m in rows %}
      <tr>
        <td><span class="pill">{{ m.kode }}</span></td>
        <td><b>{{ m.nama }}</b></td>
        <td>{{ m.alamat or '-' }}</td>
        <td>{{ m.tgl_daftar }}</td>
        <td><span class="pill {{ 'orange' if (m.pinjam_aktif or 0) > 0 else 'green' }}">{{ m.pinjam_aktif or 0 }}/{{ max_pinjam }}</span></td>
        <td>{{ m.jumlah_pinjam or 0 }} transaksi</td>
        <td>
          <div class="actions">
            <a class="btn btn-light" href="{{ url_for('member_edit', member_id=m.id) }}">Edit</a>
            <form method="post" action="{{ url_for('member_delete', member_id=m.id) }}">
              <button class="btn btn-danger" data-confirm="Hapus anggota '{{ m.nama }}'?">Hapus</button>
            </form>
          </div>
        </td>
      </tr>
      {% else %}
      <tr><td colspan="7" class="empty">Belum ada data anggota.</td></tr>
      {% endfor %}
      </tbody></table></div>
    </section>
    """
    return page("Data Anggota", "members", render_template_string(content, rows=rows, q=q, max_pinjam=MAX_PINJAM_AKTIF))

@app.route("/anggota/export.csv")
def export_members():
    with get_db() as db:
        rows = db.execute("SELECT kode, nama, alamat, tgl_daftar FROM anggota ORDER BY kode ASC").fetchall()
    return csv_response(
        "data_anggota_pustakaku.csv",
        ["Kode", "Nama Anggota", "Alamat", "Tanggal Daftar"],
        [[r["kode"], r["nama"], r["alamat"] or "", r["tgl_daftar"]] for r in rows]
    )

MEMBER_FORM = """
<section class="panel"><div class="panel-head"><div><h3>{{ heading }}</h3><div class="muted">Format kode anggota disarankan AGTxx atau Axxx</div></div></div>
<form method="post"><div class="form-grid">
<div class="field"><label>Kode Anggota</label><input name="kode" required maxlength="10" {{ 'readonly' if mode=='edit' else '' }} value="{{ member.kode if member else '' }}" placeholder="Contoh: AGT05"></div>
<div class="field"><label>Nama Lengkap</label><input name="nama" required maxlength="80" value="{{ member.nama if member else '' }}" placeholder="Nama anggota"></div>
<div class="field"><label>Tanggal Daftar</label><input type="date" name="tgl_daftar" required value="{{ member.tgl_daftar if member else today }}"></div>
<div class="field"><label>Alamat</label><input name="alamat" maxlength="140" value="{{ member.alamat if member and member.alamat else '' }}" placeholder="Alamat domisili"></div>
</div><div class="form-actions"><button class="btn">Simpan Anggota</button><a class="btn btn-light" href="{{ url_for('members') }}">Batal</a></div></form></section>
"""

@app.route("/anggota/tambah", methods=["GET", "POST"])
def member_new():
    if request.method == "POST":
        kode = request.form.get("kode", "").strip().upper()
        nama = request.form.get("nama", "").strip()
        alamat = request.form.get("alamat", "").strip()
        tgl_daftar = request.form.get("tgl_daftar", "").strip() or date.today().isoformat()
        if not re.fullmatch(r"[A-Za-z]{1,4}\d{2,4}", kode):
            flash("Kode anggota harus berformat huruf + angka, contoh AGT05.", "danger")
        elif not nama:
            flash("Nama anggota wajib diisi.", "danger")
        else:
            try:
                with get_db() as db:
                    db.execute("INSERT INTO anggota (kode,nama,alamat,tgl_daftar) VALUES (?,?,?,?)", (kode, nama, alamat, tgl_daftar))
                flash("Anggota berhasil ditambahkan.", "success")
                return redirect(url_for("members"))
            except sqlite3.IntegrityError:
                flash("Kode anggota sudah digunakan.", "danger")

    return page("Tambah Anggota", "members", render_template_string(MEMBER_FORM, heading="Tambah Anggota Baru", member=None, mode="tambah", today=date.today().isoformat()))

@app.route("/anggota/edit/<int:member_id>", methods=["GET", "POST"])
def member_edit(member_id):
    with get_db() as db:
        member = db.execute("SELECT * FROM anggota WHERE id=?", (member_id,)).fetchone()
        if not member:
            flash("Data anggota tidak ditemukan.", "warning")
            return redirect(url_for("members"))
        if request.method == "POST":
            nama = request.form.get("nama", "").strip()
            alamat = request.form.get("alamat", "").strip()
            tgl_daftar = request.form.get("tgl_daftar", "").strip() or member["tgl_daftar"]
            if not nama:
                flash("Nama anggota wajib diisi.", "danger")
            else:
                db.execute("UPDATE anggota SET nama=?, alamat=?, tgl_daftar=? WHERE id=?", (nama, alamat, tgl_daftar, member_id))
                flash("Data anggota berhasil diperbarui.", "success")
                return redirect(url_for("members"))

    return page("Edit Anggota", "members", render_template_string(MEMBER_FORM, heading="Edit Data Anggota", member=member, mode="edit", today=date.today().isoformat()))

@app.route("/anggota/hapus/<int:member_id>", methods=["POST"])
def member_delete(member_id):
    with get_db() as db:
        member = db.execute("SELECT nama FROM anggota WHERE id=?", (member_id,)).fetchone()
        if not member:
            flash("Data anggota tidak ditemukan.", "warning")
            return redirect(url_for("members"))
        used = db.execute(
            "SELECT COUNT(*) FROM peminjaman WHERE anggota_id=? OR nama_peminjam=?",
            (member_id, member["nama"])
        ).fetchone()[0]
        if used:
            flash("Anggota tidak dapat dihapus karena memiliki riwayat peminjaman.", "danger")
        else:
            db.execute("DELETE FROM anggota WHERE id=?", (member_id,))
            flash("Data anggota berhasil dihapus.", "success")
    return redirect(url_for("members"))

# =========================
# PEMINJAMAN + PENGEMBALIAN + KETERLAMBATAN + EXPORT
# =========================
@app.route("/peminjaman")
def loans():
    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    with get_db() as db:
        rows = db.execute("""
            SELECT p.*, b.judul, b.kode
            FROM peminjaman p
            JOIN buku b ON b.id = p.buku_id
            WHERE p.nama_peminjam LIKE ? OR b.judul LIKE ? OR b.kode LIKE ?
            ORDER BY p.id DESC
        """, (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()

    filtered = []
    for r in rows:
        item = dict(r)
        telat = hitung_hari_terlambat(r["tanggal_kembali"], r["status"])
        denda = hitung_denda(telat)
        item["hari_telat"] = telat
        item["denda"] = denda
        item["denda_fmt"] = format_rupiah(denda)
        if status_filter == "Dipinjam" and r["status"] != "Dipinjam":
            continue
        if status_filter == "Dikembalikan" and r["status"] != "Dikembalikan":
            continue
        if status_filter == "Terlambat" and telat <= 0:
            continue
        filtered.append(item)

    content = """
    <section class="panel">
      <div class="panel-head">
        <div><h3>Data Peminjaman</h3><div class="muted">Pantau transaksi, keterlambatan, estimasi denda ({{ denda_fmt }}/hari), dan pengembalian buku</div></div>
        <div class="panel-actions">
          <a class="btn btn-light" href="{{ url_for('export_loans') }}">⬇ Export CSV</a>
          <a class="btn" href="{{ url_for('loan_new') }}">＋ Pinjam Buku</a>
        </div>
      </div>
      <form class="toolbar" method="get">
        <input class="search" name="q" value="{{ q }}" placeholder="Cari peminjam, judul, atau kode buku...">
        <select class="filter-select" name="status" onchange="this.form.submit()">
          <option value="" {{ 'selected' if status_filter=='' else '' }}>Semua Status</option>
          <option value="Dipinjam" {{ 'selected' if status_filter=='Dipinjam' else '' }}>Dipinjam</option>
          <option value="Terlambat" {{ 'selected' if status_filter=='Terlambat' else '' }}>Terlambat</option>
          <option value="Dikembalikan" {{ 'selected' if status_filter=='Dikembalikan' else '' }}>Dikembalikan</option>
        </select>
        <button class="btn btn-light">Cari</button>
        {% if q or status_filter %}<a class="btn btn-light" href="{{ url_for('loans') }}">Reset</a>{% endif %}
      </form>
      <div class="table-wrap"><table><thead><tr><th>PEMINJAM</th><th>BUKU</th><th>TGL PINJAM</th><th>BATAS KEMBALI</th><th>TGL KEMBALI</th><th>DENDA</th><th>STATUS</th><th>AKSI</th></tr></thead><tbody>
      {% for p in rows %}
      <tr>
        <td><b>{{ p.nama_peminjam }}</b></td>
        <td>{{ p.judul }}<span class="sub">{{ p.kode }}</span></td>
        <td>{{ p.tanggal_pinjam }}</td>
        <td>{{ p.tanggal_kembali }}</td>
        <td>{{ p.tanggal_dikembalikan or '-' }}</td>
        <td>{{ p.denda_fmt if p.denda > 0 else '-' }}</td>
        <td>
          {% if p.status == 'Dikembalikan' %}
            <span class="pill green">Dikembalikan</span>
          {% elif p.hari_telat > 0 %}
            <span class="pill red">Terlambat {{ p.hari_telat }} hari</span>
          {% else %}
            <span class="pill orange">Dipinjam</span>
          {% endif %}
        </td>
        <td>
          <div class="actions">
            {% if p.status == 'Dipinjam' %}
              <form method="post" action="{{ url_for('loan_return', loan_id=p.id) }}">
                <button class="btn btn-success" data-confirm="Tandai buku '{{ p.judul }}' sudah dikembalikan?">Kembalikan</button>
              </form>
            {% endif %}
            <form method="post" action="{{ url_for('loan_delete', loan_id=p.id) }}">
              <button class="btn btn-danger" data-confirm="Hapus transaksi peminjaman ini?">Hapus</button>
            </form>
          </div>
        </td>
      </tr>
      {% else %}
      <tr><td colspan="8" class="empty">Belum ada data peminjaman yang sesuai.</td></tr>
      {% endfor %}
      </tbody></table></div>
    </section>
    """
    return page("Peminjaman", "loans", render_template_string(
        content, rows=filtered, q=q, status_filter=status_filter, denda_fmt=format_rupiah(DENDA_PER_HARI)
    ))

@app.route("/peminjaman/export.csv")
def export_loans():
    with get_db() as db:
        rows = db.execute("""
            SELECT p.*, b.judul, b.kode
            FROM peminjaman p
            JOIN buku b ON b.id = p.buku_id
            ORDER BY p.id DESC
        """).fetchall()
    data_rows = []
    for r in rows:
        telat = hitung_hari_terlambat(r["tanggal_kembali"], r["status"])
        denda = hitung_denda(telat)
        data_rows.append([
            r["id"], r["nama_peminjam"], r["kode"], r["judul"],
            r["tanggal_pinjam"], r["tanggal_kembali"], r["tanggal_dikembalikan"] or "",
            r["status"], telat, denda
        ])
    return csv_response(
        "data_peminjaman_pustakaku.csv",
        ["ID", "Peminjam", "Kode Buku", "Judul Buku", "Tanggal Pinjam", "Batas Kembali", "Tanggal Dikembalikan", "Status", "Hari Terlambat", "Estimasi Denda"],
        data_rows
    )

@app.route("/peminjaman/tambah", methods=["GET", "POST"])
def loan_new():
    with get_db() as db:
        available = db.execute("SELECT * FROM buku WHERE stok > 0 ORDER BY judul").fetchall()
        members_list = db.execute("SELECT * FROM anggota ORDER BY nama").fetchall()

        if request.method == "POST":
            anggota_id = request.form.get("anggota_id", "").strip()
            nama_manual = request.form.get("nama_peminjam", "").strip()
            buku_id = request.form.get("buku_id", "").strip()
            tanggal_pinjam = request.form.get("tanggal_pinjam", "").strip()
            tanggal_kembali = request.form.get("tanggal_kembali", "").strip()

            anggota_row = db.execute("SELECT * FROM anggota WHERE id=?", (anggota_id,)).fetchone() if anggota_id else None
            nama_final = anggota_row["nama"] if anggota_row else nama_manual

            if not nama_final or not buku_id or not tanggal_pinjam or not tanggal_kembali:
                flash("Mohon lengkapi peminjam, buku, dan tanggal transaksi.", "danger")
            elif tanggal_kembali < tanggal_pinjam:
                flash("Batas pengembalian tidak boleh lebih awal dari tanggal pinjam.", "danger")
            else:
                aktif_count = db.execute(
                    "SELECT COUNT(*) FROM peminjaman WHERE status='Dipinjam' AND nama_peminjam=?",
                    (nama_final,)
                ).fetchone()[0]
                if aktif_count >= MAX_PINJAM_AKTIF:
                    flash(f"{nama_final} sudah mencapai batas maksimal {MAX_PINJAM_AKTIF} buku yang sedang dipinjam.", "danger")
                else:
                    try:
                        db.execute("BEGIN IMMEDIATE")
                        book = db.execute("SELECT * FROM buku WHERE id=?", (buku_id,)).fetchone()
                        if not book or book["stok"] < 1:
                            db.rollback()
                            flash("Stok buku habis atau buku tidak ditemukan.", "danger")
                        else:
                            db.execute("""
                                INSERT INTO peminjaman (anggota_id, nama_peminjam, buku_id, tanggal_pinjam, tanggal_kembali, status)
                                VALUES (?, ?, ?, ?, ?, 'Dipinjam')
                            """, (anggota_row["id"] if anggota_row else None, nama_final, buku_id, tanggal_pinjam, tanggal_kembali))
                            db.execute("UPDATE buku SET stok = stok - 1 WHERE id = ?", (buku_id,))
                            db.commit()
                            flash("Transaksi peminjaman berhasil dicatat dan stok buku diperbarui.", "success")
                            return redirect(url_for("loans"))
                    except sqlite3.Error as err:
                        db.rollback()
                        flash(f"Gagal memproses transaksi: {err}", "danger")

    content = """
    <section class="panel"><div class="panel-head"><div><h3>Form Peminjaman Buku</h3><div class="muted">Pilih anggota terdaftar atau ketik nama peminjam manual (maks. {{ max_pinjam }} pinjaman aktif)</div></div></div>
    {% if not available %}<div class="flash warning">Stok semua buku sedang habis. Tambahkan stok terlebih dahulu.</div>{% endif %}
    <form method="post"><div class="form-grid">
    <div class="field"><label>Pilih Anggota Terdaftar (Opsional)</label>
      <select name="anggota_id">
        <option value="">-- Pilih anggota --</option>
        {% for m in members_list %}<option value="{{ m.id }}">{{ m.kode }} - {{ m.nama }}</option>{% endfor %}
      </select>
    </div>
    <div class="field"><label>Nama Peminjam (Jika Tidak Memilih Dropdown)</label>
      <input name="nama_peminjam" placeholder="Contoh: Muhammad Nabil">
    </div>
    <div class="field full"><label>Pilih Buku (Stok Tersedia)</label>
      <select name="buku_id" required>
        <option value="">-- Pilih buku --</option>
        {% for b in available %}<option value="{{ b.id }}">{{ b.kode }} - {{ b.judul }} (stok {{ b.stok }})</option>{% endfor %}
      </select>
    </div>
    <div class="field"><label>Tanggal Pinjam</label><input type="date" name="tanggal_pinjam" required value="{{ today }}"></div>
    <div class="field"><label>Batas Pengembalian</label><input type="date" name="tanggal_kembali" required value="{{ due }}"></div>
    </div><div class="form-actions"><button class="btn" {% if not available %}disabled{% endif %}>Simpan Peminjaman</button><a class="btn btn-light" href="{{ url_for('loans') }}">Batal</a></div></form></section>
    """
    today = date.today().isoformat()
    due = (date.today() + timedelta(days=7)).isoformat()
    return page("Tambah Peminjaman", "loans", render_template_string(
        content, available=available, members_list=members_list, today=today, due=due, max_pinjam=MAX_PINJAM_AKTIF
    ))

@app.route("/peminjaman/kembali/<int:loan_id>", methods=["POST"])
def loan_return(loan_id):
    with get_db() as db:
        try:
            db.execute("BEGIN IMMEDIATE")
            loan = db.execute("SELECT * FROM peminjaman WHERE id=?", (loan_id,)).fetchone()
            if not loan or loan["status"] != "Dipinjam":
                db.rollback()
                flash("Transaksi tidak ditemukan atau sudah dikembalikan.", "warning")
            else:
                db.execute(
                    "UPDATE peminjaman SET status='Dikembalikan', tanggal_dikembalikan=? WHERE id=?",
                    (date.today().isoformat(), loan_id)
                )
                db.execute("UPDATE buku SET stok = stok + 1 WHERE id=?", (loan["buku_id"],))
                db.commit()
                flash("Buku berhasil dikembalikan dan stok bertambah.", "success")
        except sqlite3.Error as err:
            db.rollback()
            flash(f"Gagal memproses pengembalian: {err}", "danger")
    return redirect(url_for("loans"))

@app.route("/peminjaman/hapus/<int:loan_id>", methods=["POST"])
def loan_delete(loan_id):
    with get_db() as db:
        try:
            db.execute("BEGIN IMMEDIATE")
            loan = db.execute("SELECT * FROM peminjaman WHERE id=?", (loan_id,)).fetchone()
            if not loan:
                db.rollback()
                flash("Transaksi tidak ditemukan.", "warning")
            else:
                if loan["status"] == "Dipinjam":
                    db.execute("UPDATE buku SET stok = stok + 1 WHERE id=?", (loan["buku_id"],))
                db.execute("DELETE FROM peminjaman WHERE id=?", (loan_id,))
                db.commit()
                flash("Transaksi berhasil dihapus.", "success")
        except sqlite3.Error as err:
            db.rollback()
            flash(f"Gagal menghapus transaksi: {err}", "danger")
    return redirect(url_for("loans"))

# =========================
# LAPORAN & REKAP
# =========================
@app.route("/laporan")
def reports():
    with get_db() as db:
        top_books = db.execute("""
            SELECT b.kode, b.judul, b.penulis, b.stok, COUNT(p.id) AS total_pinjam
            FROM buku b
            LEFT JOIN peminjaman p ON p.buku_id = b.id
            GROUP BY b.id
            ORDER BY total_pinjam DESC, b.kode ASC
            LIMIT 5
        """).fetchall()

        top_borrowers = db.execute("""
            SELECT nama_peminjam,
                   COUNT(*) AS total_transaksi,
                   SUM(CASE WHEN status='Dipinjam' THEN 1 ELSE 0 END) AS sedang_dipinjam
            FROM peminjaman
            GROUP BY nama_peminjam
            ORDER BY total_transaksi DESC, nama_peminjam ASC
            LIMIT 5
        """).fetchall()

        active_loans = db.execute("""
            SELECT p.*, b.kode, b.judul
            FROM peminjaman p
            JOIN buku b ON b.id = p.buku_id
            WHERE p.status = 'Dipinjam'
            ORDER BY p.tanggal_kembali ASC
        """).fetchall()

    late_list = []
    total_denda = 0
    for r in active_loans:
        telat = hitung_hari_terlambat(r["tanggal_kembali"], r["status"])
        if telat > 0:
            denda = hitung_denda(telat)
            total_denda += denda
            item = dict(r)
            item["hari_telat"] = telat
            item["denda_fmt"] = format_rupiah(denda)
            late_list.append(item)

    content = """
    <section class="stats">
      <div class="stat"><div class="stat-top"><span>Transaksi Keterlambatan</span><span class="stat-icon">⏰</span></div><strong>{{ late_count }}</strong><small>Melewati batas kembali</small></div>
      <div class="stat"><div class="stat-top"><span>Estimasi Denda Berjalan</span><span class="stat-icon">💰</span></div><strong>{{ total_denda_fmt }}</strong><small>Tarif {{ tarif_fmt }}/hari</small></div>
      <div class="stat"><div class="stat-top"><span>Buku Terpopuler</span><span class="stat-icon">🏆</span></div><strong>{{ top_books[0].judul if top_books and top_books[0].total_pinjam > 0 else '-' }}</strong><small>{{ top_books[0].total_pinjam if top_books else 0 }}x dipinjam</small></div>
      <div class="stat"><div class="stat-top"><span>Peminjam Teraktif</span><span class="stat-icon">🌟</span></div><strong>{{ top_borrowers[0].nama_peminjam if top_borrowers else '-' }}</strong><small>{{ top_borrowers[0].total_transaksi if top_borrowers else 0 }} transaksi</small></div>
    </section>

    <section class="panel">
      <div class="panel-head"><div><h3>Rekap Keterlambatan Aktif</h3><div class="muted">Daftar transaksi yang melewati batas waktu pengembalian</div></div></div>
      <div class="table-wrap"><table><thead><tr><th>PEMINJAM</th><th>BUKU</th><th>BATAS KEMBALI</th><th>HARI TERLAMBAT</th><th>ESTIMASI DENDA</th></tr></thead><tbody>
      {% for l in late_list %}
      <tr>
        <td><b>{{ l.nama_peminjam }}</b></td>
        <td>{{ l.judul }}<span class="sub">{{ l.kode }}</span></td>
        <td>{{ l.tanggal_kembali }}</td>
        <td><span class="pill red">{{ l.hari_telat }} hari</span></td>
        <td><b>{{ l.denda_fmt }}</b></td>
      </tr>
      {% else %}
      <tr><td colspan="5" class="empty">Tidak ada transaksi yang terlambat saat ini.</td></tr>
      {% endfor %}
      </tbody></table></div>
    </section>

    <div class="info-grid">
      <section class="panel" style="margin-bottom:0">
        <div class="panel-head"><div><h3>5 Buku Paling Sering Dipinjam</h3></div></div>
        <div class="table-wrap"><table><thead><tr><th>BUKU</th><th>STOK</th><th>FREKUENSI</th></tr></thead><tbody>
        {% for tb in top_books %}
        <tr><td><b>{{ tb.judul }}</b><span class="sub">{{ tb.kode }} · {{ tb.penulis }}</span></td><td>{{ tb.stok }}</td><td><span class="pill">{{ tb.total_pinjam }}x</span></td></tr>
        {% endfor %}
        </tbody></table></div>
      </section>

      <section class="panel" style="margin-bottom:0">
        <div class="panel-head"><div><h3>5 Peminjam Paling Aktif</h3></div></div>
        <div class="table-wrap"><table><thead><tr><th>PEMINJAM</th><th>AKTIF</th><th>TOTAL</th></tr></thead><tbody>
        {% for tp in top_borrowers %}
        <tr><td><b>{{ tp.nama_peminjam }}</b></td><td>{{ tp.sedang_dipinjam or 0 }}</td><td><span class="pill green">{{ tp.total_transaksi }}x</span></td></tr>
        {% else %}
        <tr><td colspan="3" class="empty">Belum ada data peminjam.</td></tr>
        {% endfor %}
        </tbody></table></div>
      </section>
    </div>
    """
    return page("Laporan & Rekap", "reports", render_template_string(
        content,
        late_count=len(late_list),
        late_list=late_list,
        total_denda_fmt=format_rupiah(total_denda),
        tarif_fmt=format_rupiah(DENDA_PER_HARI),
        top_books=top_books,
        top_borrowers=top_borrowers
    ))

# =========================
# TENTANG SISTEM
# =========================
@app.route("/tentang")
def about():
    content = """
    <section class="panel">
      <div class="panel-head"><div><h3>Tentang Sistem PustakaKu</h3><div class="muted">Implementasi CRUD Sistem Informasi Perpustakaan berbasis Python Flask & SQLite</div></div></div>
      <div class="info-grid">
        <div class="info-box">
          <h4>Modul & Operasi CRUD</h4>
          <ul>
            <li><b>Data Buku:</b> Create, Read, Update, Delete, pencarian, filter kategori, dan Export CSV.</li>
            <li><b>Data Anggota:</b> Create, Read, Update, Delete, penghitungan pinjaman aktif, dan Export CSV.</li>
            <li><b>Peminjaman & Laporan:</b> Catat pinjam, filter status/keterlambatan, hitung denda, proses kembali, hapus transaksi, rekap laporan, dan Export CSV.</li>
          </ul>
        </div>
        <div class="info-box">
          <h4>Aturan Bisnis & Integritas Data</h4>
          <ul>
            <li>Stok buku otomatis berkurang saat peminjaman disimpan dan bertambah saat buku dikembalikan atau transaksi aktif dihapus.</li>
            <li>Buku dengan stok 0 tidak dapat dipinjamkan, dan anggota dibatasi maksimal {{ max_pinjam }} buku aktif.</li>
            <li>Buku atau anggota yang sudah memiliki riwayat peminjaman tidak dapat dihapus sembarangan.</li>
          </ul>
        </div>
      </div>
    </section>
    """
    return page("Tentang Sistem", "about", render_template_string(content, max_pinjam=MAX_PINJAM_AKTIF))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)