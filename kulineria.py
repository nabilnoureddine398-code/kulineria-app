import streamlit as st
import random
import time
import pandas as pd
import json
import os
import urllib.parse

# -----------------------------------------------------------------------------
# INTEGRASI FITUR BARU 6: DATABASE PERMANEN (JSON LOCAL STORAGE) & SINKRONISASI
# -----------------------------------------------------------------------------
DB_FILE = "kulineria_db.json"

def load_permanent_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_permanent_db():
    db_data = {
        "inventory_stock": st.session_state.inventory_stock,
        "transaction_history": st.session_state.transaction_history,
        "reviews": st.session_state.reviews,
        "wishlist": st.session_state.wishlist,
        "table_status": {str(k): v for k, v in st.session_state.table_status.items()},
        "promos": st.session_state.promos
    }
    try:
        with open(DB_FILE, "w") as f:
            json.dump(db_data, f, indent=4)
    except Exception as e:
        pass

# Inisialisasi Database Permanen di Awal
db_loaded = load_permanent_db()

# -----------------------------------------------------------------------------
# INTEGRASI FITUR BARU 5: GENERATOR LAPORAN PDF ASLI (REPORTLAB / FPDF ENGINE)
# -----------------------------------------------------------------------------
def generate_native_pdf_bytes(branch_name, transactions):
    try:
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,
            spaceAfter=10
        )
        elements.append(Paragraph("<b>KULINERIA ENTERPRISE SYSTEM</b>", title_style))
        elements.append(Paragraph(f"<b>Laporan Rekapitulasi Tutup Buku (PDF Asli Engine)</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))

        total_rev = sum(trx.get("total", 0) for trx in transactions)
        info_text = f"""
        <b>Cabang Operasional:</b> {branch_name}<br/>
        <b>Waktu Cetak:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Total Transaksi Sukses:</b> {len(transactions)}<br/>
        <b>Total Pendapatan Kasir:</b> Rp {total_rev:,}
        """
        elements.append(Paragraph(info_text, styles['Normal']))
        elements.append(Spacer(1, 15))

        table_data = [["No", "Waktu", "Pelanggan", "WA", "Status", "Metode", "Total (Rp)"]]
        for idx, t in enumerate(transactions):
            table_data.append([
                str(idx + 1),
                str(t.get("waktu", "-")),
                str(t.get("nama", "-")),
                str(t.get("wa", "-")),
                str(t.get("status", "Selesai")),
                str(t.get("metode", "-")),
                f"Rp {t.get('total', 0):,}"
            ])

        if len(table_data) == 1:
            table_data.append(["-", "-", "Belum ada data transaksi", "-", "-", "-", "0"])

        t_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ])
        t_table = Table(table_data, colWidths=[25, 110, 80, 85, 75, 75, 80])
        t_table.setStyle(t_style)
        elements.append(t_table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        return None

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="Kulineria - Professional Food Finder & POS System",
    page_icon="🍔",
    layout="wide"
)

# ==========================================
# 2. CSS Paksa Ganti Warna Background & Tampilan Card
st.markdown("""
<style>
    /* 1. LATAR BELAKANG UTAMA (Cerah, Warm & Elegan - Tidak Pucat/Polos) */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%) !important;
    }

    /* 2. AREA KONTEN UTAMA (Kartu Putih Elegan dengan Bayangan Halus) */
    .stMainBlockContainer {
        background-color: #ffffff !important;
        border-radius: 20px !important;
        padding: 2.5rem !important;
        box-shadow: 0 10px 30px rgba(234, 88, 12, 0.08) !important;
        border: 1px solid #ffedd5 !important;
        margin-top: 1rem !important;
    }

    /* 3. SIDEBAR KIRI (Putih Clean Elegan & Berjarak Rapi) */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 2px solid #fed7aa !important;
        box-shadow: 4px 0 15px rgba(0,0,0,0.02) !important;
    }

    /* 4. SERAGAMKAN SEMUA WARNA TULISAN DI SELURUH APLIKASI (SERAGAM, TAJAM, BISA DIBACA) */
    h1, h2, h3, h4, h5, h6, 
    p, span, label, div, 
    .stMarkdown, [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] *, 
    .stRadio label span {
        color: #0f172a !important; /* Warna Navy Slate Pekat & Sangat Jelas */
        font-family: 'Inter', -apple-system, sans-serif !important;
        font-weight: 600 !important;
    }

    /* 5. FIX TOMBOL LOGOUT & TOMBOL LAINNYA BIAR TULISAN & WARNANYA MERAH CERAH SEGAR */
    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25) !important;
        padding: 0.6rem 1.2rem !important;
    }

    div.stButton > button * {
        color: #ffffff !important; /* Paksa teks tombol tetap putih jelas */
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(239, 68, 68, 0.35) !important;
    }

    /* 6. KOTAK PROMO / BANNER INFO (Kuning Oranye Cerah) */
    .stAlert {
        background-color: #fef3c7 !important;
        border: 2px solid #fde047 !important;
        border-radius: 16px !important;
    }
    .stAlert * {
        color: #9a3412 !important;
    }
</style>
""", unsafe_allow_html=True)
# Inisialisasi Session State
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "reviews" not in st.session_state:
    st.session_state.reviews = db_loaded["reviews"] if db_loaded and "reviews" in db_loaded else []

if "transaction_history" not in st.session_state:
    st.session_state.transaction_history = db_loaded["transaction_history"] if db_loaded and "transaction_history" in db_loaded else []

if "wishlist" not in st.session_state:
    st.session_state.wishlist = db_loaded["wishlist"] if db_loaded and "wishlist" in db_loaded else []

# Status Meja Resto (Grid Visual)
if "table_status" not in st.session_state:
    if db_loaded and "table_status" in db_loaded:
        st.session_state.table_status = {int(k): v for k, v in db_loaded["table_status"].items()}
    else:
        st.session_state.table_status = {i: "🟢 Kosong" for i in range(1, 11)}

# Inisialisasi Session State Stok Menu Angka Riil
if "inventory_stock" not in st.session_state:
    if db_loaded and "inventory_stock" in db_loaded:
        st.session_state.inventory_stock = db_loaded["inventory_stock"]
    else:
        st.session_state.inventory_stock = {
            "Ayam Geprek Sambal Korek Lvl 5": 25,
            "Bebek Goreng Madura Bumbu Hitam": 15,
            "Tahu Tek Telur Petis Surabaya": 30,
            "Rawon Sapi Daging Empal": 10,
            "Seblak Jeletot Komplit": 20,
            "Es Kopi Susu Gula Aren Signature": 40,
            "Matcha Latte Creamy Cheese": 25,
            "Es Pisang Ijo Karamel Lumer": 18,
            "Es Cendol Durian Kental": 12,
            "Es Teh Manis Jumbo": 50,
        }

# -----------------------------------------------------------------------------
# INTEGRASI FITUR BARU 7: DATA PROMO AKTIF
# -----------------------------------------------------------------------------
if "promos" not in st.session_state:
    if db_loaded and "promos" in db_loaded:
        st.session_state.promos = db_loaded["promos"]
    else:
        st.session_state.promos = [
            {"kode": "UNESA10", "nama": "Promo Mahasiswa UNESA (10%)", "tipe": "persen", "val": 0.10},
            {"kode": "OPEN5K", "nama": "Diskon Grand Opening (Rp 5.000)", "tipe": "nominal", "val": 5000},
            {"kode": "VIP20", "nama": "Diskon Spesial VIP (20%)", "tipe": "persen", "val": 0.20}
        ]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = "Pembeli"

if "selected_branch" not in st.session_state:
    st.session_state.selected_branch = "Cabang Ketintang (Dekat UNESA)"

# ==========================================
# FITUR 1: HALAMAN LOGIN / SELEKSI ROLE TERPISAH
# ==========================================
if not st.session_state.logged_in:
    st.title("🔐 Login Akses - Kulineria Enterprise Suite")
    st.markdown("Silakan pilih peran akses masuk ke dalam sistem aplikasi.")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.info("👤 **Akses Pembeli / Pelanggan**\n\nEksplorasi kuliner, gacha, resep, kalkulator ongkir, wishlist, dan pelacakan pesanan.")
        if st.button("Masuk sebagai Pembeli"):
            st.session_state.logged_in = True
            st.session_state.role = "Pembeli"
            st.rerun()
            
    with col_l2:
        st.success("👨‍💼 **Akses Kasir / Admin**\n\nTerminal POS lengkap dengan grid meja real-time, QRIS scan HP, diskon promo, dan laporan PDF.")
        pass_code = st.text_input("PIN Admin / Kasir:", type="password")
        if st.button("Masuk sebagai Kasir"):
            if pass_code == "1234": # PIN default kasir
                st.session_state.logged_in = True
                st.session_state.role = "Kasir"
                st.rerun()
            else:
                st.error("PIN salah! Gunakan '1234' untuk masuk sebagai Kasir.")
    st.stop()

# Tombol Logout di Sidebar atas
if st.sidebar.button("🔒 Logout / Ganti Akun"):
    st.session_state.logged_in = False
    st.rerun()

# Database Cabang & Link Google Maps Riil (Sidoarjo & Surabaya)
branch_data = {
    "Cabang Ketintang (Dekat UNESA)": {
        "alamat": "Jl. Ketintang Madya No. 3 (Dekat Kampus UNESA)", 
        "lat": -7.3012, "lon": 112.7334
    },
    "Cabang Waru - Sidoarjo": {
        "alamat": "Jl. Raya Waru No. 88, Sidoarjo", 
        "lat": -7.3572, "lon": 112.7291
    },
    "Cabang Gubeng - Surabaya Pusat": {
        "alamat": "Jl. Raya Gubeng No. 50, Surabaya", 
        "lat": -7.2691, "lon": 112.7512
    }
}

st.sidebar.markdown("---")
st.sidebar.subheader("📍 Pilih Cabang Aktif")
selected_b = st.sidebar.selectbox("Titik Lokasi Cabang:", list(branch_data.keys()), index=list(branch_data.keys()).index(st.session_state.selected_branch))
st.session_state.selected_branch = selected_b
st.sidebar.caption(f"📌 Alamat: {branch_data[selected_b]['alamat']}")

# Judul & Header Profesional
st.title(f"🍔 Kulineria: Enterprise Food Finder & POS Suite")
st.markdown(f"**Status Sesi Berjalan:** 🟢 Login sebagai `{{{st.session_state.role.upper()}}}` | **Cabang Aktif:** `{st.session_state.selected_branch}`")

# -----------------------------------------------------------------------------
# INTEGRASI FITUR BARU 7: NOTIFIKASI PROMO BANNER BANNER
# -----------------------------------------------------------------------------
st.info("📢 **PROMO SPESIAL HARI INI:** Gunakan kode promo `UNESA10` untuk Diskon 10% atau `OPEN5K` untuk potongan Rp 5.000!")
st.markdown("---")

# ==========================================
# PEMISAHAN TAMPILAN MENU BERDASARKAN ROLE
# ==========================================
st.sidebar.title("🍽️ Navigasi Menu")

if st.session_state.role == "Kasir":
    st.sidebar.success("👨‍💼 Mode: Panel Kontrol Kasir")
    menu = st.sidebar.radio("Pilih Menu Kasir:", [
        "📊 Dashboard & Grafik Pendapatan",
        "💳 Terminal Kasir, Diskon & QRIS (POS)",
        "🪑 Monitor Status Meja Real-Time",
        "📦 Manajemen Stok Nominal Angka",
        "🧾 Laporan Tutup Buku (PDF)",
        "🏷️ Manajemen Promo & Analisis Menu" # FITUR TAMBAHAN 7
    ])
else:
    st.sidebar.info("👤 Mode: Portal Pelanggan")
    menu = st.sidebar.radio("Pilih Menu Pelanggan:", [
        "🎲 Gacha Makanan",
        "🌶️ Radar Kuliner & Filter Wilayah",
        "🍳 Resep Kreasi Unik",
        "🧮 Kalkulator Estimasi Ongkir",
        "❤️ Wishlist Menu Favorit",
        "🛒 Keranjang & Checkout Mandiri",
        "📦 Status Pesanan Saya",
        "⭐ Catat & Review Resto"
    ])

# Statistik Live di Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📈 Status Sistem")
st.sidebar.metric(label="Total Resto Ter-review", value=len(st.session_state.reviews))
st.sidebar.metric(label="Total Transaksi Kasir", value=len(st.session_state.transaction_history))
st.sidebar.metric(label="Item di Keranjang", value=sum(item["qty"] for item in st.session_state.cart.values()))

# Identitas Footer di Sidebar
st.sidebar.markdown("---")
st.sidebar.info(
    "**D4 Manajemen Informatika**\n\n"
    "Universitas Negeri Surabaya (UNESA)\n\n"
    "*Project Tugas Kelompok 2026*"
)

# ==========================================
# 0. MENU KASIR: DASHBOARD & GRAFIK PENDAPATAN
# ==========================================
if menu == "📊 Dashboard & Grafik Pendapatan":
    st.header("📊 Dashboard Analitik & Grafik Pendapatan Kasir")
    st.markdown("Monitoring performa keuangan secara visual dan real-time.")
    
    col_d1, col_d2, col_d3 = st.columns(3)
    total_pendapatan = sum(trx["total"] for trx in st.session_state.transaction_history)
    
    col_d1.metric("💰 Total Pendapatan", f"Rp {total_pendapatan:,}")
    col_d2.metric("⭐ Total Review Resto", len(st.session_state.reviews))
    col_d3.metric("🛍️ Transaksi Sukses", len(st.session_state.transaction_history))
    
    st.markdown("---")
    st.subheader("📈 Grafik Tren Pendapatan per Transaksi")
    if st.session_state.transaction_history:
        chart_data = pd.DataFrame({
            "Transaksi": [f"Nota #{i+1}" for i in range(len(st.session_state.transaction_history))],
            "Total Pendapatan (Rp)": [trx["total"] for trx in st.session_state.transaction_history]
        })
        st.bar_chart(chart_data.set_index("Transaksi"))
    else:
        info_chart = pd.DataFrame({"Pendapatan": [0]}, index=["Belum Ada Transaksi"])
        st.bar_chart(info_chart)
        st.info("Belum ada data transaksi untuk ditampilkan ke dalam grafik.")

    st.markdown("---")
    st.subheader("📋 Log Riwayat Transaksi Sukses")
    if not st.session_state.transaction_history:
        st.info("Belum ada transaksi kasir yang diselesaikan.")
    else:
        for idx, trx in enumerate(reversed(st.session_state.transaction_history)):
            real_idx = len(st.session_state.transaction_history) - 1 - idx
            with st.expander(f"Nota #{real_idx + 1} — Pelanggan: {trx['nama']} ({trx.get('tipe_pesanan', 'Dine-In')}) - Rp {trx['total']:,}"):
                st.write(f"**Cabang:** {trx.get('cabang', 'Cabang Ketintang')}")
                st.write(f"**Metode Pembayaran:** {trx['metode']}")
                st.write(f"**Waktu Transaksi:** {trx['waktu']}")
                st.write(f"**Diskon Diberikan:** {trx.get('diskon_info', 'Tanpa Diskon')}")
                
                # FITUR TAMBAHAN 1 & 3: WhatsApp & Status Pesanan di Riwayat
                st.write(f"**No WhatsApp Pelanggan:** {trx.get('wa', '-')}")
                st.write(f"**Status Pesanan:** `{trx.get('status', 'Diproses')}`")
                
                # FITUR TAMBAHAN 3: KASIR BISA MENGUBAH STATUS PESANAN REAL-TIME
                new_status = st.selectbox(
                    "Ubah Status Pesanan:",
                    ["Diproses Kasir", "Sedang Dimasak", "Siap Disajikan / Dikirim", "Selesai"],
                    index=["Diproses Kasir", "Sedang Dimasak", "Siap Disajikan / Dikirim", "Selesai"].index(trx.get('status', 'Diproses Kasir')) if trx.get('status') in ["Diproses Kasir", "Sedang Dimasak", "Siap Disajikan / Dikirim", "Selesai"] else 0,
                    key=f"status_change_{real_idx}"
                )
                if new_status != trx.get('status'):
                    st.session_state.transaction_history[real_idx]['status'] = new_status
                    save_permanent_db()
                    st.toast("Status pesanan berhasil diperbarui!", icon="✅")
                    st.rerun()

                st.write("**Detail Pembelian:**")
                for item_dtl in trx['items']:
                    st.text(f"- {item_dtl}")

# ==========================================
# 1. MENU KASIR: TERMINAL KASIR & QRIS SCAN (POS)
# ==========================================
elif menu == "💳 Terminal Kasir, Diskon & QRIS (POS)":
    st.header("💳 POS (Point of Sales) — Terminal Kasir & QRIS")
    st.markdown(f"Sistem kasir digital cabang **{st.session_state.selected_branch}** lengkap dengan QRIS scan HP & diskon promo.")
    
    daftar_menu = [
        {"item": "Ayam Geprek Sambal Korek Lvl 5", "kategori": "Makanan", "harga": 18000},
        {"item": "Bebek Goreng Madura Bumbu Hitam", "kategori": "Makanan", "harga": 25000},
        {"item": "Tahu Tek Telur Petis Surabaya", "kategori": "Makanan", "harga": 15000},
        {"item": "Rawon Sapi Daging Empal", "kategori": "Makanan", "harga": 28000},
        {"item": "Seblak Jeletot Komplit", "kategori": "Makanan", "harga": 16000},
        {"item": "Es Kopi Susu Gula Aren Signature", "kategori": "Minuman", "harga": 18000},
        {"item": "Matcha Latte Creamy Cheese", "kategori": "Minuman", "harga": 20000},
        {"item": "Es Pisang Ijo Karamel Lumer", "kategori": "Minuman / Dessert", "harga": 12000},
        {"item": "Es Cendol Durian Kental", "kategori": "Minuman / Dessert", "harga": 14000},
        {"item": "Es Teh Manis Jumbo", "kategori": "Minuman", "harga": 5000},
    ]
    
    col_menu, col_struk = st.columns([1.4, 1.1])
    
    with col_menu:
        st.subheader("🛒 Katalog Menu Kasir (Stok Riil)")
        for index, item in enumerate(daftar_menu):
            item_name = item['item']
            stok_sisa = st.session_state.inventory_stock.get(item_name, 0)
            
            c1, c2, c3 = st.columns([2.0, 1.2, 1.1])
            c1.write(f"**{item_name}**\n*(Stok: {stok_sisa} porsi)*")
            c2.write(f"Rp {item['harga']:,}")
            
            if stok_sisa > 0:
                if c3.button("➕ Tambah", key=f"kasir_btn_{index}"):
                    st.session_state.inventory_stock[item_name] -= 1
                    if item_name in st.session_state.cart:
                        st.session_state.cart[item_name]["qty"] += 1
                    else:
                        st.session_state.cart[item_name] = {"harga": item['harga'], "qty": 1, "kategori": item['kategori']}
                    save_permanent_db()
                    st.toast(f"{item_name} ditambahkan!", icon="🛒")
                    st.rerun()
            else:
                c3.warning("Habis")

    with col_struk:
        st.subheader("📋 Keranjang Belanja & Pembayaran")
        
        if not st.session_state.cart:
            st.info("Keranjang kasir masih kosong.")
        else:
            subtotal_harga = 0
            struk_text = f"======== KULINERIA POS ({st.session_state.selected_branch}) ========\n"
            list_item_trx = []
            
            for item_name, info in list(st.session_state.cart.items()):
                sub_item = info["harga"] * info["qty"]
                subtotal_harga += sub_item
                
                c_name, c_qty, c_del = st.columns([1.8, 1.2, 0.8])
                c_name.write(f"**{item_name}**\nRp {info['harga']:,} x {info['qty']}")
                
                if c_qty.button("➖", key=f"sub_{item_name}"):
                    st.session_state.cart[item_name]["qty"] -= 1
                    st.session_state.inventory_stock[item_name] += 1
                    if st.session_state.cart[item_name]["qty"] <= 0:
                        del st.session_state.cart[item_name]
                    save_permanent_db()
                    st.rerun()
                    
                if c_del.button("🗑️ Hapus", key=f"del_{item_name}"):
                    st.session_state.inventory_stock[item_name] += info["qty"]
                    del st.session_state.cart[item_name]
                    save_permanent_db()
                    st.rerun()
                    
                struk_text += f"{item_name} (x{info['qty']}) : Rp {sub_item:,}\n"
                list_item_trx.append(f"{item_name} (x{info['qty']}) = Rp {sub_item:,}")
            
            st.markdown("---")
            
            tipe_pesanan = st.radio("Tipe Pesanan:", ["🍽️ Dine-In (Makan di Tempat)", "🛍️ Takeaway (Bungkus)"])
            nomor_meja = 1
            if "Dine-In" in tipe_pesanan:
                nomor_meja = st.selectbox("Pilih Nomor Meja Dine-In:", list(range(1, 11)))

            pilihan_diskon = st.selectbox("Voucher / Promo Diskon:", [
                "Tanpa Diskon", 
                "Promo Mahasiswa UNESA (10%)", 
                "Diskon Grand Opening (Rp 5.000)", 
                "Diskon Spesial VIP (20%)"
            ])
            
            potongan = 0
            if pilihan_diskon == "Promo Mahasiswa UNESA (10%)":
                potongan = int(subtotal_harga * 0.10)
            elif pilihan_diskon == "Diskon Grand Opening (Rp 5.000)":
                potongan = 5000
            elif pilihan_diskon == "Diskon Spesial VIP (20%)":
                potongan = int(subtotal_harga * 0.20)
                
            total_akhir = max(0, subtotal_harga - potongan)
            
            st.write(f"Subtotal: Rp {subtotal_harga:,}")
            if potongan > 0:
                st.write(f"Potongan Diskon: - Rp {potongan:,}")
            st.markdown(f"### **Total Tagihan: Rp {total_akhir:,}**")
            
            struk_text += f"-------------------------------------\nSubtotal: Rp {subtotal_harga:,}\nDiskon: - Rp {potongan:,}\nTOTAL: Rp {total_akhir:,}\nTipe: {tipe_pesanan} (Meja: {nomor_meja})\n"
            
            metode = st.selectbox("Metode Pembayaran:", ["Tunai (Cash)", "QRIS All Payment", "DANA", "ShopeePay", "OVO", "GoPay"])
            nama_pelanggan = st.text_input("Nama Pelanggan:", "Nabil")
            
            # FITUR TAMBAHAN 1: WHATSAPP PELANGGAN
            wa_pelanggan = st.text_input("📱 Nomor WhatsApp Pelanggan (contoh: 08123456789):", "08123456789")
            
            struk_text += f"Pelanggan: {nama_pelanggan}\nNo WA: {wa_pelanggan}\nMetode: {metode}\n====================================="
            
            if metode == "Tunai (Cash)":
                nominal_cash = st.number_input("Bayar Tunai (Rp):", min_value=total_akhir, value=total_akhir, step=5000)
                kembalian = nominal_cash - total_akhir
                st.write(f"Uang Kembalian: **Rp {kembalian:,}**")
            elif metode == "QRIS All Payment":
                # Gambar QR Code Asli (Bisa Di-scan Kamera HP)
                st.info("📱 **Silakan Scan QRIS berikut menggunakan m-banking / e-wallet HP:**")
                st.image(
                    "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=KULINERIA_PAYMENT_QRIS",
                    caption="Scan QRIS Dinamis untuk menyelesaikan pembayaran",
                    width=200
                )
                # FITUR TAMBAHAN 2: KONFIRMASI PEMBAYARAN QRIS KASIR
                qris_confirm = st.checkbox("✅ Konfirmasi Pembayaran QRIS Diterima & Valid", value=True)
            else:
                st.text_input(f"No HP / Akun {metode}:", wa_pelanggan)

            col_bayar, col_reset = st.columns(2)
            with col_bayar:
                if st.button("✅ Selesaikan & Cetak"):
                    with st.spinner("Memproses transaksi..."):
                        time.sleep(1)
                    st.snow()
                    st.success("🎉 Transaksi Berhasil Direkam!")
                    
                    if "Dine-In" in tipe_pesanan:
                        st.session_state.table_status[nomor_meja] = f"🔴 Terisi ({nama_pelanggan})"

                    new_trx = {
                        "nama": nama_pelanggan,
                        "wa": wa_pelanggan, # FITUR TAMBAHAN 1
                        "total": total_akhir,
                        "metode": metode,
                        "items": list_item_trx,
                        "cabang": st.session_state.selected_branch,
                        "tipe_pesanan": f"{tipe_pesanan} (Meja {nomor_meja})",
                        "diskon_info": pilihan_diskon,
                        "status": "Diproses Kasir", # FITUR TAMBAHAN 3
                        "waktu": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.transaction_history.append(new_trx)
                    save_permanent_db() # FITUR TAMBAHAN 4 & 6: SINKRONISASI & PERMANEN DB
                    
                    st.download_button(
                        label="📄 Download Struk .TXT",
                        data=struk_text,
                        file_name=f"Struk_{nama_pelanggan}.txt",
                        mime="text/plain"
                    )
                    
                    # FITUR TAMBAHAN 1: LINK KIRIM STRUK KE WA
                    msg_wa = f"Halo {nama_pelanggan}, Terima kasih telah memesan di Kulineria ({st.session_state.selected_branch})!\nTotal Pembayaran: Rp {total_akhir:,} ({metode}). Status pesananmu sedang diproses!"
                    encoded_wa = urllib.parse.quote(msg_wa)
                    wa_url = f"https://wa.me/{wa_pelanggan.replace('08', '628')}?text={encoded_wa}"
                    st.markdown(f"[💬 Kirim Nota Struk ke WhatsApp Pelanggan]({wa_url})", unsafe_allow_html=True)

                    import streamlit.components.v1 as components
                    html_print_code = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <script>
                            function triggerPrint() {{
                                var myWindow = window.open('', '_blank', 'width=400,height=600');
                                myWindow.document.write('<html><head><title>Struk Kulineria</title></head><body style="font-family:monospace; padding:20px;">');
                                myWindow.document.write('<h3><center>KULINERIA ENTERPRISE POS</center></h3>');
                                myWindow.document.write('<p>Cabang: {st.session_state.selected_branch}<br>Waktu: {time.strftime("%Y-%m-%d %H:%M:%S")}<br>Pelanggan: {nama_pelanggan}<br>Tipe: {tipe_pesanan}</p>');
                                myWindow.document.write('<hr>');
                                myWindow.document.write('<pre>{struk_text.replace(chr(10), "<br>")}</pre>');
                                myWindow.document.write('<hr>');
                                myWindow.document.write('<p align="center">Terima Kasih!<br>D4 Manajemen Informatika UNESA</p>');
                                myWindow.document.write('</body></html>');
                                myWindow.document.close();
                                myWindow.focus();
                                setTimeout(function(){{myWindow.print();}}, 500);
                            }}
                        </script>
                    </head>
                    <body style="margin:0; padding:0;">
                        <button onclick="triggerPrint()" style="width:100%; background-color:#ff4b4b; color:white; padding:12px; border:none; border-radius:6px; font-weight:bold; font-family:sans-serif; cursor:pointer;">
                            🖨️ Klik Disini Untuk Cetak Struk
                        </button>
                    </body>
                    </html>
                    """
                    components.html(html_print_code, height=60)
            with col_reset:
                if st.button("🗑️ Kosongkan Keranjang"):
                    for k, v in st.session_state.cart.items():
                        st.session_state.inventory_stock[k] += v["qty"]
                    st.session_state.cart = {}
                    save_permanent_db()
                    st.rerun()

# ==========================================
# 2. MENU KASIR: MONITOR STATUS MEJA REAL-TIME
# ==========================================
elif menu == "🪑 Monitor Status Meja Real-Time":
    st.header("🪑 Monitor Status Ketersediaan Meja Resto")
    st.markdown(f"Grid visual real-time status meja untuk **{st.session_state.selected_branch}**.")
    
    st.info("💡 Klik tombol di bawah untuk mengubah status meja menjadi Kosong kembali setelah pelanggan selesai.")
    st.markdown("---")
    
    cols = st.columns(5)
    for meja_id, status_val in st.session_state.table_status.items():
        col_idx = (meja_id - 1) % 5
        with cols[col_idx]:
            st.metric(label=f"Meja #{meja_id}", value=status_val)
            if "Terisi" in status_val:
                if st.button(f"Kosongkan Meja {meja_id}", key=f"clear_table_{meja_id}"):
                    st.session_state.table_status[meja_id] = "🟢 Kosong"
                    save_permanent_db()
                    st.rerun()

# ==========================================
# 3. MENU KASIR: MANAJEMEN STOK NOMINAL ANGKA
# ==========================================
elif menu == "📦 Manajemen Stok Nominal Angka":
    st.header("📦 Manajemen Stok Nominal Angka Cabang")
    st.markdown(f"Atur jumlah nominal ketersediaan stok fisik harian untuk **{st.session_state.selected_branch}**.")
    
    st.info("💡 Ubah angka nominal di bawah ini untuk menambah atau mengurangi stok secara langsung.")
    st.markdown("---")
    
    for menu_item, stock_val in st.session_state.inventory_stock.items():
        col_s1, col_s2 = st.columns([2, 1])
        col_s1.write(f"**{menu_item}**")
        new_stock = col_s2.number_input(f"Stok {menu_item}", min_value=0, max_value=500, value=stock_val, key=f"stock_num_{menu_item}", label_visibility="collapsed")
        if new_stock != stock_val:
            st.session_state.inventory_stock[menu_item] = new_stock
            save_permanent_db()

    st.success("✅ Perubahan stok nominal angka berhasil disinkronkan ke sistem POS.")

# ==========================================
# 4. MENU KASIR: LAPORAN TUTUP BUKU (PDF)
# ==========================================
elif menu == "🧾 Laporan Tutup Buku (PDF)":
    st.header("🧾 Laporan Rekap Tutup Buku (End of Shift — PDF)")
    st.markdown("Generate dokumen laporan rekapitulasi keuangan harian berformat PDF siap cetak.")
    
    total_trx_count = len(st.session_state.transaction_history)
    total_rev = sum(trx["total"] for trx in st.session_state.transaction_history)
    
    st.subheader(f"📌 Ringkasan Shift Aktif — {st.session_state.selected_branch}")
    st.write(f"* **Waktu Cetak Laporan:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"* **Total Nota Selesai:** {total_trx_count} Transaksi")
    st.write(f"* **Akumulasi Kas Masuk:** Rp {total_rev:,}")
    
    st.markdown("---")
    
    # FITUR TAMBAHAN 5: DOWLOAD PDF ASLI (REPORTLAB PDF ENGINE)
    pdf_bytes = generate_native_pdf_bytes(st.session_state.selected_branch, st.session_state.transaction_history)
    if pdf_bytes:
        st.download_button(
            label="📄 Download Laporan PDF Asli (.PDF File)",
            data=pdf_bytes,
            file_name=f"Laporan_TutupBuku_{time.strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )

    html_report_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Laporan Tutup Buku Kulineria</title>
        <style>
            body {{ font-family: Helvetica, Arial, sans-serif; padding: 30px; color: #333; }}
            h2, h4 {{ text-align: center; color: #2c3e50; }}
            hr {{ border: 1px solid #ccc; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <h2>KULINERIA ENTERPRISE SYSTEM</h2>
        <h4>Laporan Rekapitulasi Tutup Buku (End of Shift)</h4>
        <hr>
        <p><strong>Cabang Operasional:</strong> {st.session_state.selected_branch}</p>
        <p><strong>Waktu Cetak:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Total Transaksi Sukses:</strong> {total_trx_count}</p>
        <p><strong>Total Pendapatan Kasir:</strong> Rp {total_rev:,}</p>
        
        <br>
        <h4>Rincian Riwayat Transaksi</h4>
        <table>
            <tr>
                <th>No</th>
                <th>Waktu</th>
                <th>Pelanggan</th>
                <th>Tipe</th>
                <th>Metode</th>
                <th>Total (Rp)</th>
            </tr>
    """
    
    if not st.session_state.transaction_history:
        html_report_content += "<tr><td colspan='6' style='text-align:center;'>Belum ada transaksi tercatat.</td></tr>"
    else:
        for i, t in enumerate(st.session_state.transaction_history):
            html_report_content += f"""
            <tr>
                <td>{i+1}</td>
                <td>{t['waktu']}</td>
                <td>{t['nama']}</td>
                <td>{t.get('tipe_pesanan', 'Dine-In')}</td>
                <td>{t['metode']}</td>
                <td>Rp {t['total']:,}</td>
            </tr>
            """
            
    html_report_content += """
        </table>
        <br><br>
        <p style="text-align: right;">Mengetahui,<br><br><br><strong>Manager / Kasir Bertugas</strong></p>
    </body>
    </html>
    """
    
    import streamlit.components.v1 as components
    import base64
    b64_html = base64.b64encode(html_report_content.encode('utf-8')).decode('utf-8')
    pdf_download_link = f"""
    <a href="data:text/html;base64,{b64_html}" download="Laporan_TutupBuku_Kulineria.html" style="display:block; text-align:center; background-color:#28a745; color:white; padding:12px; text-decoration:none; border-radius:6px; font-weight:bold; font-family:sans-serif;">
        📥 Download / Cetak Laporan Dokumen HTML
    </a>
    """
    components.html(pdf_download_link, height=60)

# ==========================================
# FITUR KASIR TAMBAHAN 7: MANAJEMEN PROMO & ANALISIS MENU
# ==========================================
elif menu == "🏷️ Manajemen Promo & Analisis Menu":
    st.header("🏷️ Manajemen Promo, Notifikasi & Analisis Menu Terlaris")
    st.markdown("Pantau analisis menu paling laku dan atur promo diskon khusus.")
    
    st.subheader("🔥 Analisis Menu Terlaris (Best Seller)")
    item_counts = {}
    for trx in st.session_state.transaction_history:
        for item_str in trx.get("items", []):
            name_part = item_str.split(" (x")[0]
            item_counts[name_part] = item_counts.get(name_part, 0) + 1
            
    if item_counts:
        df_analytics = pd.DataFrame(list(item_counts.items()), columns=["Menu", "Frekuensi Dipesan"]).sort_values(by="Frekuensi Dipesan", ascending=False)
        st.bar_chart(df_analytics.set_index("Menu"))
    else:
        st.info("Belum ada data penjualan untuk analisis menu.")

    st.markdown("---")
    st.subheader("➕ Tambah Voucher Promo Baru")
    with st.form("form_promo"):
        p_kode = st.text_input("Kode Promo (contoh: KULINER20):")
        p_nama = st.text_input("Deskripsi Promo:", "Diskon Khusus 20%")
        p_tipe = st.selectbox("Tipe Diskon:", ["persen", "nominal"])
        p_val = st.number_input("Nilai Diskon (0.1 = 10%, atau angka nominal Rp):", min_value=0.0, value=0.1)
        
        if st.form_submit_button("Simpan Promo"):
            st.session_state.promos.append({"kode": p_kode, "nama": p_nama, "tipe": p_tipe, "val": p_val})
            save_permanent_db()
            st.success(f"Promo `{p_kode}` berhasil dibuat!")
            st.rerun()

# ==========================================
# 5. MENU PEMBELI: GACHA MAKANAN
# ==========================================
elif menu == "🎲 Gacha Makanan":
    st.header("🎲 Gacha Kuliner: Solusi Cepat Bingung Makan")
    st.markdown("Pilih preferensi rasa dan biarkan sistem mengundi menu terbaik untukmu!")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        mood = st.selectbox("Lagi Pengen Sensasi Rasa Apa?", ["Semua Rasa", "Pedas Nampol 🌶️", "Gurih / Asin 🍗", "Manis / Dessert 🍧", "Kuah Segar 🍲", "Minuman Kekinian 🧋"])
        porsi = st.radio("Kategori Porsi:", ["Camilan Ringan", "Makan Siang / Malam Kenyang", "Porsi Rame-rame Kelompok"])
        
        makanan_db = {
            "Pedas Nampol 🌶️": ["Ayam Geprek Sambal Korek Level 5", "Seblak Jeletot Komplit Extra Ceker", "Pentol Gila Pedas Cadas", "Rujak Cingur Sambal Petis Pedas"],
            "Gurih / Asin 🍗": ["Nasi Goreng Mawut Sosis Kebuli", "Tahu Tek Telur Petis khas Surabaya", "Bebek Goreng Madura Bumbu Hitam", "Martabak Telur Daging Sapi Special"],
            "Manis / Dessert 🍧": ["Es Pisang Ijo Karamel Lumer", "Kue Pukis Keeling Lumer Keju", "Terang Bulan Red Velvet Cream Cheese", "Es Cendol Durian Kental"],
            "Kuah Segar 🍲": ["Soto Ayam Lamongan Koya Melimpah", "Rawon Sapi Daging Empal Bumbu Hitam", "Bakso Malang Komplit Paru Kering", "Mie Kocok Bandung Kuah Kikil"],
            "Minuman Kekinian 🧋": ["Es Kopi Susu Gula Aren Signature", "Matcha Latte Creamy Cheese Foam", "Jus Mangga Segar Extra Whipped Cream", "Thai Tea Original Bangkok"]
        }
        
        if st.button("🎰 Putar Undian Gacha!"):
            with st.spinner("Mengacak algoritma kuliner..."):
                time.sleep(1.2)
            if mood == "Semua Rasa":
                pilihan = random.choice([item for sublist in makanan_db.values() for item in sublist])
            else:
                pilihan = random.choice(makanan_db[mood])
                
            st.balloons()
            st.success(f"🎉 **Rekomendasi Terpilih:** {pilihan}")
            st.info(f"Target Porsi: **{porsi}** di **{st.session_state.selected_branch}**.")

    with col2:
        st.subheader("💡 Catatan Gacha")
        st.info("Fitur ini dirancang menggunakan algoritma acak untuk mengatasi keraguan memilih makanan.")

# ==========================================
# 6. MENU PEMBELI: RADAR KULINER & FILTER WILAYAH
# ==========================================
elif menu == "🌶️ Radar Kuliner & Filter Wilayah":
    st.header("🌶️ Radar Kuliner Unik & Legendaris Nusantara")
    st.markdown("Eksplorasi kuliner lokal. Dilengkapi filter wilayah spesifik (Ketintang/Waru/Gubeng) dan link Google Maps!")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_wilayah = st.selectbox("Filter Wilayah:", ["Semua Wilayah", "Area Ketintang (UNESA)", "Area Sidoarjo / Waru", "Area Surabaya Pusat (Gubeng)"])
    with col_f2:
        filter_kategori = st.selectbox("Filter Kategori:", ["Semua Kategori", "Makanan Berat", "Minuman / Dessert", "Camilan Tradisional"])
    with col_f3:
        filter_harga = st.selectbox("Filter Batas Harga:", ["Semua Harga", "Di bawah Rp 15.000", "Di bawah Rp 30.000"])
    
    data_kuliner = [
        {"nama": "🍢 Sate Lalat", "kategori": "Camilan Tradisional", "wilayah": "Area Sidoarjo / Waru", "asal": "Pamekasan, Madura", "desc": "Sate potongan kecil mirip lalat dengan bumbu kacang pekat khas Madura.", "harga": 12000, "unik": "8.5 / 10", "badge": "🔥 Unik", "maps_link": "https://maps.google.com/?q=Sate+Lalat+Madura+Surabaya"},
        {"nama": "🍲 Rawon Setan", "kategori": "Makanan Berat", "wilayah": "Area Surabaya Pusat (Gubeng)", "asal": "Surabaya, Jawa Timur", "desc": "Rawon kuah pekat kluwek hitam dengan daging empuk besar dan sambal pedas.", "harga": 28000, "unik": "9.0 / 10", "badge": "🏆 Legendaris", "maps_link": "https://maps.google.com/?q=Rawon+Setan+Embong+Malang+Surabaya"},
        {"nama": "🍧 Es Laksamana Mengamuk", "kategori": "Minuman / Dessert", "wilayah": "Area Ketintang (UNESA)", "asal": "Riau", "desc": "Minuman segar buah kuini dipadu kuah santan gurih dan gula merah.", "harga": 15000, "unik": "9.8 / 10", "badge": "⭐ Segar", "maps_link": "https://maps.google.com/?q=Kuliner+Pekanbaru+Riau"},
        {"nama": "🍛 Nasi Bebek Bumbu Hitam", "kategori": "Makanan Berat", "wilayah": "Area Ketintang (UNESA)", "asal": "Bangkalan, Madura", "desc": "Nasi hangat dengan bebek empuk berlumur bumbu hitam rempah pekat.", "harga": 25000, "unik": "9.2 / 10", "badge": "👑 Favorit", "maps_link": "https://maps.google.com/?q=Bebek+Sinjay+Surabaya+Ketintang"},
        {"nama": "🧋 Es Kopi Susu Gula Aren", "kategori": "Minuman / Dessert", "wilayah": "Area Ketintang (UNESA)", "asal": "Surabaya", "desc": "Perpaduan espresso pilihan dengan susu segar dan gula aren asli.", "harga": 18000, "unik": "9.5 / 10", "badge": "☕ Best Seller", "maps_link": "https://maps.google.com/?q=Kopi+Kenangan+Ketintang+Surabaya"}
    ]
    
    st.markdown("---")
    for idx, item in enumerate(data_kuliner):
        pass_wil = (filter_wilayah == "Semua Wilayah" or item["wilayah"] == filter_wilayah)
        pass_kat = (filter_kategori == "Semua Kategori" or item["kategori"] == filter_kategori)
        pass_hrg = True
        if filter_harga == "Di bawah Rp 15.000" and item["harga"] > 15000: pass_hrg = False
        elif filter_harga == "Di bawah Rp 30.000" and item["harga"] > 30000: pass_hrg = False
            
        if pass_wil and pass_kat and pass_hrg:
            with st.expander(f"{item['nama']} — {item['wilayah']} ({item['badge']})", expanded=True):
                col_info1, col_info2, col_info3, col_info4 = st.columns([2.2, 0.9, 0.9, 1])
                with col_info1:
                    st.write(item["desc"])
                    st.write(f"💰 Rp {item['harga']:,} | ✨ Unik: `{item['unik']}`")
                with col_info2:
                    st.markdown(f"[📍 Maps]({item['maps_link']})", unsafe_allow_html=True)
                with col_info3:
                    if st.button("❤️ Favorit", key=f"fav_{idx}"):
                        if item['nama'] not in st.session_state.wishlist:
                            st.session_state.wishlist.append(item['nama'])
                            save_permanent_db()
                            st.toast(f"{item['nama']} disimpan ke Wishlist!", icon="❤️")
                with col_info4:
                    item_name = item['nama']
                    st.session_state.inventory_stock.setdefault(item_name, 5)
                    stok_radar = st.session_state.inventory_stock.get(item_name, 5)
                    if stok_radar > 0:
                        if st.button("➕ Pesan", key=f"radar_{idx}"):
                            st.session_state.inventory_stock[item_name] -= 1
                            if item_name in st.session_state.cart:
                                st.session_state.cart[item_name]["qty"] += 1
                            else:
                                st.session_state.cart[item_name] = {"harga": item['harga'], "qty": 1, "kategori": item['kategori']}
                            save_permanent_db()
                            st.toast(f"{item_name} masuk keranjang!", icon="🛒")
                            st.rerun()
                    else:
                        st.warning("Stok Habis")

# ==========================================
# 7. MENU PEMBELI: RESEP KREASI UNIK
# ==========================================
elif menu == "🍳 Resep Kreasi Unik":
    st.header("🍳 Resep Kreasi Kuliner Kreatif & Praktis")
    st.markdown("Panduan memasak lengkap dengan kalkulator takaran bahan otomatis berdasarkan jumlah porsi.")
    
    resep_pilihan = st.selectbox("Pilih Resep:", [
        "Indomie Carbonara Keju Creamy",
        "Nasi Goreng Kimchi Jawa (Pedas Manis)",
        "Omelet Mie Geprek Lumer",
        "Es Kopi Susu Gula Aren Signature"
    ])
    
    porsi = st.number_input("🔢 Masukkan Jumlah Porsi / Gelas:", min_value=1, max_value=100, value=1, step=1)
    st.info(f"✨ Takaran bahan di bawah ini otomatis disesuaikan untuk **{porsi} Porsi/Gelas**:")
    st.markdown("---")
    
    if resep_pilihan == "Indomie Carbonara Keju Creamy":
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.subheader("🍝 Indomie Carbonara Keju Creamy")
            st.info("⏱️ Waktu: 10 Menit | Kesulitan: Mudah")
            st.markdown(f"* Bungkus Indomie Goreng: **{1 * porsi} bungkus**\n* Susu UHT full cream: **{100 * porsi} ml**\n* Keju melt slice: **{1 * porsi} lembar**")
        with col_r2:
            st.subheader("👨‍🍳 Langkah Pembuatan:")
            st.markdown("1. Rebus mie setengah matang, tiriskan.\n2. Panaskan susu UHT, masukkan bumbu dan keju.\n3. Campurkan mie ke saus creamy.")
            
    elif resep_pilihan == "Nasi Goreng Kimchi Jawa (Pedas Manis)":
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.subheader("🍚 Nasi Goreng Kimchi Jawa")
            st.info("⏱️ Waktu: 12 Menit | Kesulitan: Sedang")
            st.markdown(f"* Piring Nasi dingin: **{1 * porsi} piring**\n* Kimchi cincang: **{3 * porsi} sdm**\n* Telur: **{1 * porsi} butir**")
        with col_r2:
            st.subheader("👨‍🍳 Langkah Pembuatan:")
            st.markdown("1. Tumis kimchi dan cabai.\n2. Masukkan telur orak-arik.\n3. Masukkan nasi dan kecap manis, aduk rata.")
            
    elif resep_pilihan == "Omelet Mie Geprek Lumer":
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.subheader("🍳 Omelet Mie Geprek Lumer")
            st.info("⏱️ Waktu: 15 Menit | Kesulitan: Mudah")
            st.markdown(f"* Mie instan: **{1 * porsi} bungkus**\n* Telur: **{2 * porsi} butir**\n* Sambal korek: **{2 * porsi} sdm**")
        with col_r2:
            st.subheader("👨‍🍳 Langkah Pembuatan:")
            st.markdown("1. Campur mie dan telur.\n2. Goreng di teflon.\n3. Oleskan sambal geprek di atasnya.")

    elif resep_pilihan == "Es Kopi Susu Gula Aren Signature":
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.subheader("🧋 Es Kopi Susu Gula Aren")
            st.info("⏱️ Waktu: 5 Menit | Kesulitan: Sangat Mudah")
            st.markdown(f"* Espresso: **{30 * porsi} ml**\n* Fresh Milk: **{120 * porsi} ml**\n* Gula Aren: **{20 * porsi} ml**")
        with col_r2:
            st.subheader("👨‍🍳 Langkah Pembuatan:")
            st.markdown("1. Masukkan gula aren dan es batu.\n2. Tuang susu fresh milk.\n3. Tambahkan espresso di atasnya.")

# ==========================================
# 8. MENU PEMBELI: KALKULATOR ESTIMASI ONGKIR
# ==========================================
elif menu == "🧮 Kalkulator Estimasi Ongkir":
    st.header("🧮 Kalkulator Estimasi Jarak & Ongkir Pengiriman")
    st.markdown("Hitung perkiraan ongkos kirim berdasarkan jarak dari cabang pilihan ke lokasi tujuanmu di Sidoarjo / Surabaya.")
    
    st.write(f"📌 **Cabang Asal Pengiriman:** `{st.session_state.selected_branch}`")
    
    jarak_km = st.slider("Estimasi Jarak Pengiriman (Kilometer):", 1.0, 25.0, 3.5, 0.5)
    tarif_per_km = 3000
    ongkir_hitung = int(jarak_km * tarif_per_km)
    
    st.info(f"🛵 **Hasil Estimasi:**")
    st.write(f"* Jarak Tempuh: **{jarak_km} KM**")
    st.write(f"* Estimasi Waktu Kurir: **{int(jarak_km * 3) + 5} Menit**")
    st.write(f"* Total Ongkir: **Rp {ongkir_hitung:,}**")

# ==========================================
# 9. MENU PEMBELI: WISHLIST MENU FAVORIT
# ==========================================
elif menu == "❤️ Wishlist Menu Favorit":
    st.header("❤️ Daftar Menu Favorit Tersimpan (Wishlist)")
    st.markdown("Kumpulan menu kuliner unik yang sudah kamu tandai sebelumnya.")
    
    if not st.session_state.wishlist:
        st.info("Belum ada menu di dalam wishlist. Yuk tandai menu kesukaanmu dari halaman Radar Kuliner!")
    else:
        for idx, w_item in enumerate(st.session_state.wishlist):
            c1, c2 = st.columns([3, 1])
            c1.write(f"✨ **{w_item}**")
            if c2.button("🗑️ Hapus", key=f"del_wish_{idx}"):
                st.session_state.wishlist.pop(idx)
                save_permanent_db()
                st.rerun()

# ==========================================
# 10. MENU PEMBELI: KERANJANG & CHECKOUT MANDIRI
# ==========================================
elif menu == "🛒 Keranjang & Checkout Mandiri":
    st.header("🛒 Keranjang Belanja & Checkout Mandiri")
    st.markdown("Kelola pesanan makanan yang sudah kamu pilih.")
    
    if not st.session_state.cart:
        st.info("Keranjang belanja kamu masih kosong.")
    else:
        total_harga = 0
        for item_name, info in list(st.session_state.cart.items()):
            subtotal = info["harga"] * info["qty"]
            total_harga += subtotal
            
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(f"**{item_name}**\nRp {info['harga']:,} x {info['qty']}")
            if c2.button("➖ Kurang", key=f"pembeli_sub_{item_name}"):
                st.session_state.cart[item_name]["qty"] -= 1
                st.session_state.inventory_stock[item_name] += 1
                if st.session_state.cart[item_name]["qty"] <= 0:
                    del st.session_state.cart[item_name]
                save_permanent_db()
                st.rerun()
            if c3.button("🗑️ Hapus", key=f"pembeli_del_{item_name}"):
                st.session_state.inventory_stock[item_name] += info["qty"]
                del st.session_state.cart[item_name]
                save_permanent_db()
                st.rerun()
                
        st.markdown("---")

        # FITUR TAMBAHAN 7: VOUCHER DISKON UNTUK PEMBELI
        kode_promo_input = st.text_input("Diskon / Kode Promo (Opsional):")
        potongan_pembeli = 0
        for p in st.session_state.promos:
            if kode_promo_input.strip().upper() == p["kode"]:
                if p["tipe"] == "persen":
                    potongan_pembeli = int(total_harga * p["val"])
                else:
                    potongan_pembeli = int(p["val"])
                st.success(f"Voucher Berhasil Dipakai: {p['nama']}")
                break
                
        total_akhir_pembeli = max(0, total_harga - potongan_pembeli)
        
        st.write(f"Subtotal: Rp {total_harga:,}")
        if potongan_pembeli > 0:
            st.write(f"Potongan Promo: - Rp {potongan_pembeli:,}")
        st.markdown(f"### **Total Pembayaran: Rp {total_akhir_pembeli:,}**")
        
        metode_bayar = st.selectbox("Pilih Metode Pembayaran:", ["QRIS All Payment", "DANA", "ShopeePay", "OVO", "GoPay", "Tunai ke Kurir"])
        nama_pemesan = st.text_input("Nama Penerima / Pemesan:", "Nabil")
        
        # FITUR TAMBAHAN 1: INPUT NO WA PEMBELI
        wa_pemesan = st.text_input("Nomor WhatsApp (Aktif):", "08123456789")
        
        if metode_bayar == "QRIS All Payment":
            st.info("📱 **Silakan Scan QRIS berikut menggunakan HP:**")
            # FITUR TAMBAHAN 2: QRIS ONLINE ASLI
            st.image(
                "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=KULINERIA_ONLINE_PAYMENT",
                caption="Scan QRIS untuk pembayaran mandiri",
                width=180
            )
            qris_buyer_confirm = st.checkbox("Saya sudah menyelesaikan transfer QRIS", value=True)

        if st.button("🚀 Konfirmasi Pesanan Mandiri"):
            st.success("🎉 Pesanan berhasil dibuat dan dikirim ke sistem cabang terdekat!")
            list_item_trx = [f"{k} (x{v['qty']}) = Rp {v['harga']*v['qty']:,}" for k, v in st.session_state.cart.items()]
            
            # FITUR TAMBAHAN 3 & 4: SINKRONISASI KE KASIR & RECORD PESANAN REAL-TIME
            st.session_state.transaction_history.append({
                "nama": nama_pemesan,
                "wa": wa_pemesan, # FITUR TAMBAHAN 1
                "total": total_akhir_pembeli,
                "metode": metode_bayar,
                "items": list_item_trx,
                "cabang": st.session_state.selected_branch,
                "tipe_pesanan": "Delivery Online",
                "status": "Menunggu Konfirmasi Kasir", # FITUR TAMBAHAN 3
                "waktu": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            st.session_state.cart = {}
            save_permanent_db() # FITUR TAMBAHAN 6
            st.balloons()

# ==========================================
# 11. MENU PEMBELI: STATUS PESANAN SAYA
# ==========================================
elif menu == "📦 Status Pesanan Saya":
    st.header("📦 Status Pelacakan Pesanan")
    st.markdown("Pantau progres pesanan makanan yang sedang diproses oleh cabang terdekat.")
    
    if not st.session_state.transaction_history:
        st.info("Kamu belum memiliki riwayat pesanan aktif.")
    else:
        # FITUR TAMBAHAN 3: KONEKSI REAL-TIME DENGAN STATUS KASIR
        for idx, trx in enumerate(reversed(st.session_state.transaction_history)):
            current_status = trx.get('status', 'Sedang Diproses')
            st.success(f"📦 Pesanan atas nama **{trx['nama']}** — Status Real-Time: **{current_status}** ⏳")
            st.write(f"* Waktu Pesan: {trx['waktu']}")
            st.write(f"* Cabang: {trx.get('cabang', 'Cabang Ketintang')}")
            st.write(f"* No WhatsApp: {trx.get('wa', '-')}")
            st.write(f"* Total: Rp {trx['total']:,} ({trx['metode']})")
            st.markdown("---")

# ==========================================
# 12. MENU PEMBELI: CATAT & REVIEW RESTO
# ==========================================
elif menu == "⭐ Catat & Review Resto":
    st.header("⭐ Buku Catatan & Ulasan Resto Favorit")
    st.markdown("Dokumentasikan tempat makan dan kuliner favoritmu dengan tautan Google Maps rute langsung.")
    
    with st.form("form_review"):
        pilihan_resto = st.selectbox("Pilih Tempat Makan / Resto:", [
            "Mie Gacoan Ketintang", "Bebek Sinjay Sidoarjo", "Ayam Geprek Pangeran", "Depot Bu Rudy Surabaya", "Warteg Kharisma Bahari", "Lainnya (Ketik Manual)"
        ])
        
        if pilihan_resto == "Lainnya (Ketik Manual)":
            nama_tempat = st.text_input("Ketik Nama Tempat Makan:")
        else:
            nama_tempat = pilihan_resto

        pilihan_menu = st.selectbox("Pilih Menu Rekomendasi:", [
            "Mie Iblis / Setan Level 3 + Es Hompimpa", "Bebek Goreng Bumbu Hitam Asli", "Ayam Geprek Sambal Korek + Nasi Hangat", "Nasi Udang Empal + Sambal Bu Rudy", "Lainnya (Ketik Manual)"
        ])
        
        if pilihan_menu == "Lainnya (Ketik Manual)":
            menu_fav = st.text_input("Ketik Menu Favorit:")
        else:
            menu_fav = pilihan_menu

        rating = st.slider("Skor Rating (1 - 5 Bintang):", 1, 5, 5)
        catatan_rasa = st.selectbox("Ringkasan Ulasan:", [
            "Rasanya enak banget, porsi pas, dan harganya ramah di kantong!",
            "Tempatnya bersih, pelayanan cepat, dan sambalnya juara pedasnya.",
            "Rasa khas banget, bikin ketagihan dan wajib dicoba lagi!"
        ])
        
        submit_review = st.form_submit_button("Simpan Ulasan")
        if submit_review:
            if nama_tempat and menu_fav:
                st.session_state.reviews.append({"tempat": nama_tempat, "menu": menu_fav, "rating": rating, "catatan": catatan_rasa})
                save_permanent_db()
                st.success(f"Ulasan untuk **{nama_tempat}** berhasil direkam!")
            else:
                st.warning("Nama tempat dan menu wajib diisi!")

    if st.session_state.reviews:
        st.subheader("📚 Daftar Resto Ter-review & Lokasi Maps")
        for r in reversed(st.session_state.reviews):
            with st.expander(f"📍 {r['tempat']} — ⭐ {r['rating']}/5"):
                st.write(f"**Menu Rekomendasi:** {r['menu']}")
                st.write(f"**Ulasan:** {r['catatan']}")
                resto_encoded = r['tempat'].replace(" ", "+")
                st.markdown(f"[🗺️ Buka Rute {r['tempat']} di Google Maps](https://maps.google.com/?q={resto_encoded}+Surabaya+Sidoarjo)", unsafe_allow_html=True)

# Footer Profesional
st.markdown("---")
st.markdown("🚀 **Kulineria Enterprise System** | D4 Manajemen Informatika - Universitas Negeri Surabaya (UNESA)")