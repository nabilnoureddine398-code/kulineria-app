import streamlit as st
import random
import time

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="Kulineria - Professional Food Finder & POS System",
    page_icon="🍔",
    layout="wide"
)

# Inisialisasi Session State
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "reviews" not in st.session_state:
    st.session_state.reviews = []

if "transaction_history" not in st.session_state:
    st.session_state.transaction_history = []

# Judul & Header Profesional
st.title("🍔 Kulineria: Enterprise Food Finder & POS Suite")
st.markdown("Platform manajemen kuliner terpadu: Eksplorasi, Resep Kreatif, Sistem Kasir POS Modern, dan Dashboard Analitik.")
st.markdown("---")

# Sidebar Navigasi Menu Profesional
st.sidebar.title("🍽️ Navigasi Kulineria")
menu = st.sidebar.radio("Pilih Menu:", [
    "📊 Dashboard & Statistik",
    "🎲 Gacha Makanan",
    "🌶️ Radar Kuliner Unik",
    "🍳 Resep Kreasi Unik",
    "💳 Kasir & Pembayaran (POS)",
    "⭐ Catat & Review Resto"
])

# Statistik Live di Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📈 Status Sistem")
st.sidebar.metric(label="Total Resto Ter-review", value=len(st.session_state.reviews))
st.sidebar.metric(label="Total Transaksi Sukses", value=len(st.session_state.transaction_history))
st.sidebar.metric(label="Item di Keranjang", value=sum(item["qty"] for item in st.session_state.cart.values()))

# ==========================================
# 0. MENU: DASHBOARD & STATISTIK
# ==========================================
if menu == "📊 Dashboard & Statistik":
    st.header("📊 Dashboard Analitik & Ringkasan Performa")
    st.markdown("Ringkasan data aktivitas aplikasi secara *real-time* untuk evaluasi dan pelaporan.")
    
    col_d1, col_d2, col_d3 = st.columns(3)
    
    total_pendapatan = sum(trx["total"] for trx in st.session_state.transaction_history)
    
    col_d1.metric("💰 Total Pendapatan Kasir", f"Rp {total_pendapatan:,}")
    col_d2.metric("⭐ Total Review Resto", len(st.session_state.reviews))
    col_d3.metric("🛍️ Transaksi Diproses", len(st.session_state.transaction_history))
    
    st.markdown("---")
    st.subheader("📋 Riwayat Transaksi Kasir Terbaru")
    
    if not st.session_state.transaction_history:
        st.info("Belum ada transaksi kasir yang diselesaikan hari ini.")
    else:
        for idx, trx in enumerate(reversed(st.session_state.transaction_history)):
            with st.expander(f"Nota #{len(st.session_state.transaction_history) - idx} — Pelanggan: {trx['nama']} (Rp {trx['total']:,})"):
                st.write(f"**Metode Pembayaran:** {trx['metode']}")
                st.write(f"**Waktu Transaksi:** {trx['waktu']}")
                st.write("**Detail Pembelian:**")
                for item_dtl in trx['items']:
                    st.text(f"- {item_dtl}")

# ==========================================
# 1. MENU: GACHA MAKANAN
# ==========================================
elif menu == "🎲 Gacha Makanan":
    st.header("🎲 Gacha Kuliner: Solusi Cepat Bingung Makan")
    st.markdown("Pilih preferensi rasa dan biarkan sistem mengundi menu terbaik untukmu!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mood = st.selectbox("Lagi Pengen Sensasi Rasa Apa?", ["Semua Rasa", "Pedas Nampol 🌶️", "Gurih / Asin 🍗", "Manis / Dessert 🍧", "Kuah Segar 🍲"])
        porsi = st.radio("Kategori Porsi:", ["Camilan Ringan", "Makan Siang / Malam Kenyang", "Porsi Rame-rame Kelompok"])
        
        makanan_db = {
            "Pedas Nampol 🌶️": ["Ayam Geprek Sambal Korek Level 5", "Seblak Jeletot Komplit Extra Ceker", "Pentol Gila Pedas Cadas", "Rujak Cingur Sambal Petis Pedas"],
            "Gurih / Asin 🍗": ["Nasi Goreng Mawut Sosis Kebuli", "Tahu Tek Telur Petis khas Surabaya", "Bebek Goreng Madura Bumbu Hitam", "Martabak Telur Daging Sapi Special"],
            "Manis / Dessert 🍧": ["Es Pisang Ijo Karamel Lumer", "Kue Pukis Keeling Lumer Keju", "Terang Bulan Red Velvet Cream Cheese", "Es Cendol Durian Kental"],
            "Kuah Segar 🍲": ["Soto Ayam Lamongan Koya Melimpah", "Rawon Sapi Daging Empal Bumbu Hitam", "Bakso Malang Komplit Paru Kering", "Mie Kocok Bandung Kuah Kikil"]
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
            st.info(f"Target Porsi: **{porsi}**.")

    with col2:
        st.subheader("💡 Catatan Gacha")
        st.info("Fitur ini dirancang menggunakan algoritma acak terstruktur untuk mengatasi keraguan memilih makanan.")

# ==========================================
# 2. MENU: RADAR KULINER UNIK
# ==========================================
elif menu == "🌶️ Radar Kuliner Unik":
    st.header("🌶️ Radar Kuliner Unik & Legendaris Nusantara")
    st.markdown("Eksplorasi kuliner antimainstream. Kamu bisa langsung menambahkan menu ini ke keranjang POS!")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_kategori = st.selectbox("Filter Kategori:", ["Semua Kategori", "Makanan Berat", "Minuman / Dessert", "Camilan Tradisional"])
    with col_f2:
        filter_harga = st.selectbox("Filter Batas Harga:", ["Semua Harga", "Di bawah Rp 15.000", "Di bawah Rp 30.000"])
    
    data_kuliner = [
        {"nama": "🍢 Sate Lalat", "kategori": "Camilan Tradisional", "asal": "Pamekasan, Madura", "desc": "Sate dengan potongan daging kecil menyerupai lalat, disajikan bumbu kacang pekat khas Madura.", "harga": 12000, "unik": "8.5 / 10", "badge": "🔥 Unik & Tradisional"},
        {"nama": "🍲 Rawon Setan", "kategori": "Makanan Berat", "asal": "Surabaya, Jawa Timur", "desc": "Rawon kuah pekat kluwek hitam dengan potongan daging empuk besar dan sambal super pedas.", "harga": 28000, "unik": "9.0 / 10", "badge": "🏆 Legendaris Jatim"},
        {"nama": "🍧 Es Laksamana Mengamuk", "kategori": "Minuman / Dessert", "asal": "Riau", "desc": "Minuman segar berbahan buah kuini/mangga dipadu kuah santan gurih dan gula merah kental.", "harga": 15000, "unik": "9.8 / 10", "badge": "⭐ Paling Segar"},
        {"nama": "🍛 Nasi Bebek Bumbu Hitam", "kategori": "Makanan Berat", "asal": "Bangkalan, Madura", "desc": "Nasi hangat dengan bebek empuk berlumur bumbu hitam rempah pekat yang gurih menggigit.", "harga": 25000, "unik": "9.2 / 10", "badge": "👑 Juara Favorit"}
    ]
    
    st.markdown("---")
    
    for idx, item in enumerate(data_kuliner):
        pass_kat = (filter_kategori == "Semua Kategori" or item["kategori"] == filter_kategori)
        pass_hrg = True
        if filter_harga == "Di bawah Rp 15.000" and item["harga"] > 15000:
            pass_hrg = False
        elif filter_harga == "Di bawah Rp 30.000" and item["harga"] > 30000:
            pass_hrg = False
            
        if pass_kat and pass_hrg:
            with st.expander(f"{item['nama']} — Asal: {item['asal']} ({item['badge']})", expanded=True):
                col_info1, col_info2 = st.columns([3, 1])
                with col_info1:
                    st.write(item["desc"])
                    st.write(f"💰 **Estimasi Harga:** Rp {item['harga']:,}")
                    st.markdown(f"✨ **Skor Keunikan:** `{item['unik']}`")
                with col_info2:
                    if st.button("➕ Masukkan POS", key=f"radar_btn_{idx}"):
                        item_name = item['nama']
                        if item_name in st.session_state.cart:
                            st.session_state.cart[item_name]["qty"] += 1
                        else:
                            st.session_state.cart[item_name] = {"harga": item['harga'], "qty": 1, "kategori": item['kategori']}
                        st.toast(f"{item_name} ditambahkan ke sistem POS!", icon="🛒")

# ==========================================
# 3. MENU: RESEP KREASI UNIK
# ==========================================
elif menu == "🍳 Resep Kreasi Unik":
    st.header("🍳 Resep Kreasi Kuliner Kreatif & Praktis")
    st.markdown("Panduan memasak langkah demi langkah untuk referensi menu kuliner mandiri.")
    
    resep_pilihan = st.selectbox("Pilih Resep:", [
        "Indomie Carbonara Keju Creamy",
        "Nasi Goreng Kimchi Jawa (Pedas Manis)",
        "Omelet Mie Geprek Lumer"
    ])
    
    st.markdown("---")
    
    if resep_pilihan == "Indomie Carbonara Keju Creamy":
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.subheader("🍝 Indomie Carbonara Keju Creamy")
            st.info("⏱️ Waktu: 10 Menit | Kesulitan: Mudah")
            st.write("**Bahan-bahan:**")
            st.markdown("""
            * 1 bungkus Indomie Goreng
            * 100 ml Susu UHT putih *full cream*
            * 1 lembar *Cheese slice* (keju melt)
            * Sosis / bakso secukupnya
            """)
        with col_r2:
            st.subheader("👨‍🍳 Langkah Pembuatan:")
            st.markdown("""
            1. Rebus mie setengah matang, lalu tiriskan airnya.
            2. Panaskan susu UHT dengan api kecil di panci terpisah.
            3. Masukkan bumbu Indomie dan keju melt hingga mengental.
            4. Campurkan mie ke dalam saus *creamy*. Siap disajikan!
            """)
            
    elif resep_pilihan == "Nasi Goreng Kimchi Jawa (Pedas Manis)":
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.subheader("🍚 Nasi Goreng Kimchi Jawa")
            st.info("⏱️ Waktu: 12 Menit | Kesulitan: Sedang")
            st.write("**Bahan-bahan:**")
            st.markdown("""
            * 1 piring Nasi dingin
            * 3 sdm Kimchi cincang
            * 1 butir Telur ayam
            * 2 sdm Kecap manis khas Jawa
            """)
        with col_r2:
            st.subheader("👨‍🍳 Langkah Pembuatan:")
            st.markdown("""
            1. Tumis kimchi cincang dan cabai hingga harum.
            2. Masukkan telur, buat orak-arik di pinggir wajan.
            3. Masukkan nasi dingin, aduk rata.
            4. Tambahkan kecap manis Jawa, aduk hingga merata sempurna.
            """)
            
    elif resep_pilihan == "Omelet Mie Geprek Lumer":
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.subheader("🍳 Omelet Mie Geprek Lumer")
            st.info("⏱️ Waktu: 15 Menit | Kesulitan: Mudah")
            st.write("**Bahan-bahan:**")
            st.markdown("""
            * 1 bungkus mie instan (rebus matang)
            * 2 butir Telur ayam
            * Sambal korek geprek secukupnya
            * Keju cheddar parut
            """)
        with col_r2:
            st.subheader("👨‍🍳 Langkah Pembuatan:")
            st.markdown("""
            1. Campur mie matang dengan telur kocok dan bumbu.
            2. Goreng di teflon dengan minyak panas hingga krispi kecokelatan.
            3. Oleskan sambal korek dan taburi keju parut di atasnya.
            """)

# ==========================================
# 4. MENU: KASIR & PEMBAYARAN (POS)
# ==========================================
elif menu == "💳 Kasir & Pembayaran (POS)":
    st.header("💳 POS (Point of Sales) & Transaksi Kasir")
    st.markdown("Sistem kasir digital lengkap dengan manajemen keranjang, diskon/total, dan pencetakan struk.")
    
    daftar_menu = [
        {"item": "Ayam Geprek Sambal Korek Lvl 5", "kategori": "Makanan", "harga": 18000},
        {"item": "Bebek Goreng Madura Bumbu Hitam", "kategori": "Makanan", "harga": 25000},
        {"item": "Tahu Tek Telur Petis Surabaya", "kategori": "Makanan", "harga": 15000},
        {"item": "Rawon Sapi Daging Empal", "kategori": "Makanan", "harga": 28000},
        {"item": "Seblak Jeletot Komplit", "kategori": "Makanan", "harga": 16000},
        {"item": "Es Pisang Ijo Karamel Lumer", "kategori": "Minuman / Dessert", "harga": 12000},
        {"item": "Es Cendol Durian Kental", "kategori": "Minuman / Dessert", "harga": 14000},
        {"item": "Es Teh Manis Jumbo", "kategori": "Minuman / Dessert", "harga": 5000},
    ]
    
    col_menu, col_struk = st.columns([1.4, 1.1])
    
    with col_menu:
        st.subheader("🛒 Katalog Menu Kasir")
        for index, item in enumerate(daftar_menu):
            c1, c2, c3 = st.columns([2.2, 1.2, 1])
            c1.write(f"**{item['item']}**\n*({item['kategori']})*")
            c2.write(f"Rp {item['harga']:,}")
            if c3.button("➕ Tambah", key=f"btn_{index}"):
                item_name = item['item']
                if item_name in st.session_state.cart:
                    st.session_state.cart[item_name]["qty"] += 1
                else:
                    st.session_state.cart[item_name] = {"harga": item['harga'], "qty": 1, "kategori": item['kategori']}
                st.toast(f"{item_name} ditambahkan!", icon="🛒")

    with col_struk:
        st.subheader("📋 Keranjang Belanja & Struk")
        
        if not st.session_state.cart:
            st.info("Keranjang kosong. Silakan pilih menu dari katalog atau menu Radar Kuliner.")
        else:
            total_harga = 0
            struk_text = "======== STRUK KULINERIA POS ========\n"
            list_item_trx = []
            
            for item_name, info in list(st.session_state.cart.items()):
                subtotal = info["harga"] * info["qty"]
                total_harga += subtotal
                
                c_name, c_qty, c_del = st.columns([1.8, 1.2, 0.8])
                c_name.write(f"**{item_name}**\nRp {info['harga']:,} x {info['qty']}")
                
                if c_qty.button("➖", key=f"sub_{item_name}"):
                    st.session_state.cart[item_name]["qty"] -= 1
                    if st.session_state.cart[item_name]["qty"] <= 0:
                        del st.session_state.cart[item_name]
                    st.rerun()
                    
                if c_del.button("🗑️ Hapus", key=f"del_{item_name}"):
                    del st.session_state.cart[item_name]
                    st.rerun()
                    
                struk_text += f"{item_name} (x{info['qty']}) : Rp {subtotal:,}\n"
                list_item_trx.append(f"{item_name} (x{info['qty']}) = Rp {subtotal:,}")
            
            st.markdown("---")
            st.markdown(f"### **Total Tagihan: Rp {total_harga:,}**")
            struk_text += f"-------------------------------------\nTOTAL: Rp {total_harga:,}\n"
            
            metode = st.selectbox("Metode Pembayaran:", [
                "Tunai (Cash)",
                "DANA",
                "ShopeePay",
                "OVO",
                "GoPay",
                "QRIS All Payment"
            ])
            
            nama_pelanggan = st.text_input("Nama Pelanggan:", "Nabil")
            struk_text += f"Pelanggan: {nama_pelanggan}\nMetode: {metode}\n====================================="
            
            if metode == "Tunai (Cash)":
                nominal_cash = st.number_input("Bayar Tunai (Rp):", min_value=total_harga, value=total_harga, step=5000)
                kembalian = nominal_cash - total_harga
                st.write(f"Uang Kembalian: **Rp {kembalian:,}**")
            elif metode == "QRIS All Payment":
                st.warning("📱 Silakan scan QRIS di layar terminal kasir.")
            else:
                st.text_input(f"No HP / Akun {metode}:", "081234567890")

            col_bayar, col_reset = st.columns(2)
            with col_bayar:
                if st.button("✅ Selesaikan & Cetak"):
                    with st.spinner("Memproses transaksi..."):
                        time.sleep(1)
                    st.snow()
                    st.success("🎉 Transaksi Berhasil Direkam!")
                    
                    # Rekam ke Riwayat Transaksi Global
                    st.session_state.transaction_history.append({
                        "nama": nama_pelanggan,
                        "total": total_harga,
                        "metode": metode,
                        "items": list_item_trx,
                        "waktu": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    st.download_button(
                        label="📄 Download Struk .TXT",
                        data=struk_text,
                        file_name=f"Struk_{nama_pelanggan}.txt",
                        mime="text/plain"
                    )
            
            with col_reset:
                if st.button("🗑️ Kosongkan Semua"):
                    st.session_state.cart = {}
                    st.rerun()

# ==========================================
# 5. MENU: CATAT & REVIEW RESTO
# ==========================================
elif menu == "⭐ Catat & Review Resto":
    st.header("⭐ Buku Catatan & Ulasan Resto Favorit")
    st.markdown("Dokumentasikan tempat makan dan kuliner favoritmu dengan cepat menggunakan form interaktif.")
    
    with st.form("form_review"):
        pilihan_resto = st.selectbox("Pilih Tempat Makan / Resto:", [
            "Mie Gacoan",
            "Bebek Sinjay Madura",
            "Ayam Geprek Pangeran",
            "Depot Bu Rudy Surabaya",
            "Warteg Kharisma Bahari",
            "Lainnya (Ketik Manual)"
        ])
        
        if pilihan_resto == "Lainnya (Ketik Manual)":
            nama_tempat = st.text_input("Ketik Nama Tempat Makan:")
        else:
            nama_tempat = pilihan_resto

        pilihan_menu = st.selectbox("Pilih Menu Rekomendasi:", [
            "Mie Iblis / Setan Level 3 + Es Hompimpa",
            "Bebek Goreng Bumbu Hitam Asli",
            "Ayam Geprek Sambal Korek + Nasi Hangat",
            "Nasi Udang Empal + Sambal Bu Rudy",
            "Paket Nasi Telur & Orek Tempe Lengkap",
            "Lainnya (Ketik Manual)"
        ])
        
        if pilihan_menu == "Lainnya (Ketik Manual)":
            menu_fav = st.text_input("Ketik Menu Favorit:")
        else:
            menu_fav = pilihan_menu

        rating = st.slider("Skor Rating (1 - 5 Bintang):", 1, 5, 5)
        
        pilihan_review = st.selectbox("Pilih Ringkasan Ulasan:", [
            "Rasanya enak banget, porsi pas, dan harganya ramah di kantong!",
            "Tempatnya bersih, pelayanan cepat, dan sambalnya juara pedasnya.",
            "Rasa khas banget, bikin ketagihan dan wajib dicoba lagi!",
            "Cukup oke buat makan bareng teman-teman sekelompok."
        ])
        catatan_rasa = pilihan_review
        
        submit_review = st.form_submit_button("Simpan Ulasan")
        if submit_review:
            if nama_tempat and menu_fav:
                st.session_state.reviews.append({
                    "tempat": nama_tempat,
                    "menu": menu_fav,
                    "rating": rating,
                    "catatan": catatan_rasa
                })
                st.success(f"Ulasan untuk **{nama_tempat}** berhasil direkam!")
            else:
                st.warning("Nama tempat dan menu wajib diisi terlebih dahulu!")

    if st.session_state.reviews:
        st.subheader("📚 Daftar Resto Ter-review")
        for r in reversed(st.session_state.reviews):
            with st.expander(f"📍 {r['tempat']} — ⭐ {r['rating']}/5"):
                st.write(f"**Menu Rekomendasi:** {r['menu']}")
                st.write(f"**Ulasan:** {r['catatan']}")

# Footer Profesional
st.markdown("---")
st.markdown("🚀 **Kulineria Enterprise System** | D4 Manajemen Informatika - Universitas Negeri Surabaya (UNESA)")