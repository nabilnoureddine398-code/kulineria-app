import streamlit as st
import random
import time

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="Kulineria - Food Finder, Rekomendasi & POS Kasir",
    page_icon="🍔",
    layout="wide"
)

# Judul Utama Aplikasi
st.title("🍔 Kulineria: Unique Food Finder & Kasir Pembayaran")
st.markdown("Aplikasi rekomendasi kuliner unik, pencatat resto favorit, serta sistem **Kasir & Pembayaran Digital (E-Wallet/Cash)**.")
st.markdown("---")

# Inisialisasi Session State untuk Keranjang Belanja Kasir
if "cart" not in st.session_state:
    st.session_state.cart = []

# Sidebar Navigasi Menu
st.sidebar.title("🍽️ Navigasi Kulineria")
menu = st.sidebar.radio("Pilih Menu:", [
    "🎲 Gacha Makanan (Bingung Makan Apa?)",
    "🌶️ Radar Kuliner Unik",
    "🍳 Resep Kreasi Unik",
    "💳 Kasir & Pembayaran (POS)",
    "⭐ Catat & Review Resto"
])

# ==========================================
# 1. MENU: GACHA MAKANAN
# ==========================================
if menu == "🎲 Gacha Makanan (Bingung Makan Apa?)":
    st.header("🎲 Bingung Mau Makan Apa Hari Ini?")
    st.markdown("Pilih selera rasa kamu dan tekan tombol di bawah untuk mengundi makanan secara acak!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mood = st.selectbox("Lagi Pengen Rasa Apa?", ["Semua Rasa", "Pedas Nampol 🌶️", "Gurih / Asin 🍗", "Manis / Dessert 🍧", "Kuah Segar 🍲"])
        porsi = st.radio("Skala Porsi Lapar:", ["Camilan Ringan", "Makan Siang / Malam kenyang", "Makan Rame-rame"])
        
        makanan_db = {
            "Pedas Nampol 🌶️": ["Ayam Geprek Sambal Korek Level 5", "Seblak Jeletot Komplit Extra Ceker", "Pentol Gila Pedas Cadas", "Rujak Cingur Sambal Petis Pedas"],
            "Gurih / Asin 🍗": ["Nasi Goreng Mawut Sosis Kebuli", "Tahu Tek Telur Petis khas Surabaya", "Bebek Goreng Madura Bumbu Hitam", "Martabak Telur Daging Sapi Special"],
            "Manis / Dessert 🍧": ["Es Pisang Ijo Karamel Lumer", "Kue Pukis Keeling Lumer Keju", "Terang Bulan Red Velvet Cream Cheese", "Es Cendol Durian Kental"],
            "Kuah Segar 🍲": ["Soto Ayam Lamongan Koya Melimpah", "Rawon Sapi Daging Empal Bumbu Hitam", "Bakso Malang Komplit Paru Kering", "Mie Kocok Bandung Kuah Kikil"]
        }
        
        if st.button("🎰 Putar Spin Makanan!"):
            if mood == "Semua Rasa":
                pilihan = random.choice([item for sublist in makanan_db.values() for item in sublist])
            else:
                pilihan = random.choice(makanan_db[mood])
                
            st.balloons()
            st.success(f"🎉 **Rekomendasi Makanan Buat Kamu:** {pilihan}")
            st.info(f"Porsi cocok untuk: **{porsi}**.")

    with col2:
        st.subheader("💡 Tips Kuliner")
        st.write("Jangan lupa minum air putih yang cukup habis makan makanan pedas atau bersantan ya!")

# ==========================================
# 2. MENU: RADAR KULINER UNIK
# ==========================================
elif menu == "🌶️ Radar Kuliner Unik":
    st.header("🌶️ Radar Kuliner Unik Indonesia")
    st.markdown("Daftar makanan dengan nama dan cita rasa unik yang wajib dicoba!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🍢 Sate Lalat")
        st.write("**Asal:** Pamekasan, Madura")
        st.write("Sate dengan potongan daging kecil-kecil menyerupai lalat, disajikan dengan bumbu kacang khas pekat.")
        st.metric("Tingkat Keunikan", "8.5 / 10")
        
    with col2:
        st.subheader("🍲 Rawon Setan")
        st.write("**Asal:** Surabaya, Jawa Timur")
        st.write("Rawon kuah pekat kluwek hitam dengan potongan daging empuk besar dan sambal pedas membakar lidah.")
        st.metric("Tingkat Pedas", "9.0 / 10")

    with col3:
        st.subheader("🍧 Es Laksamana Mengamuk")
        st.write("**Asal:** Riau")
        st.write("Minuman segar berbahan utama buah kuini/mangga dipadu kuah santan gurih dan gula merah pekat.")
        st.metric("Tingkat Kesegaran", "9.8 / 10")

# ==========================================
# 3. MENU: RESEP KREASI UNIK
# ==========================================
elif menu == "🍳 Resep Kreasi Unik":
    st.header("🍳 Resep Kreasi Makanan Unik & Praktis")
    
    resep_pilihan = st.selectbox("Pilih Resep yang Mau Dilihat:", [
        "Indomie Carbonara Keju Creamy",
        "Nasi Goreng Kimchi Jawa (Pedas Manis)",
        "Omelet Mie Geprek Lumer"
    ])
    
    if resep_pilihan == "Indomie Carbonara Keju Creamy":
        st.subheader("🍝 Indomie Carbonara Keju Creamy")
        st.write("**Bahan:** 1 bungkus Indomie, 100ml susu UHT putih, 1 lembar keju melt, sosis/bakso.")
        st.markdown("""
        1. Rebus mie setengah matang, buang air rebusannya.
        2. Tuang susu UHT ke dalam panci mie.
        3. Masukkan bumbu Indomie dan keju melt.
        4. Aduk hingga kuah susu dan keju mengental *creamy*. Siap disajikan!
        """)
    elif resep_pilihan == "Nasi Goreng Kimchi Jawa (Pedas Manis)":
        st.subheader("🍚 Nasi Goreng Kimchi Jawa")
        st.write("**Bahan:** Nasi dingin, kimchi, kecap manis Jawa, telur, dan cabai rawit.")
        st.markdown("""
        1. Tumis kimchi cincang dan cabai rawit sampai harum.
        2. Masukkan nasi dan telur orak-arik.
        3. Tambahkan bumbu kimchi dan sentuhan kecap manis khas Jawa. Aduk rata!
        """)
    elif resep_pilihan == "Omelet Mie Geprek Lumer":
        st.subheader("🍳 Omelet Mie Geprek Lumer")
        st.write("**Bahan:** 1 bungkus mie instan, 2 butir telur, sambal korek geprek, keju parut.")
        st.markdown("""
        1. Campur mie rebus matang dengan telur dan bumbu, lalu goreng hingga garing.
        2. Oleskan sambal korek geprek pedas di atas omelet.
        3. Taburi keju parut di atasnya selagi panas.
        """)

# ==========================================
# 4. MENU: KASIR & PEMBAYARAN (POS)
# ==========================================
elif menu == "💳 Kasir & Pembayaran (POS)":
    st.header("💳 Kasir & Pemesanan Kulineria")
    st.markdown("Pilih menu makanan/minuman, pesan, dan bayar dengan metode **Cash atau E-Wallet**.")
    
    # Daftar Menu & Harga
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
    
    col_menu, col_struk = st.columns([1.5, 1])
    
    with col_menu:
        st.subheader("🛒 Pilih Menu Pesanan")
        for index, item in enumerate(daftar_menu):
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(f"**{item['item']}** ({item['kategori']})")
            c2.write(f"Rp {item['harga']:,}")
            if c3.button("➕ Tambah", key=f"btn_{index}"):
                st.session_state.cart.append(item)
                st.toast(f"{item['item']} ditambahkan ke keranjang!", icon="🛒")

    with col_struk:
        st.subheader("📋 Ringkasan Struk")
        
        if len(st.session_state.cart) == 0:
            st.info("Keranjang belanjaan masih kosong.")
        else:
            total_harga = 0
            for idx, cart_item in enumerate(st.session_state.cart):
                st.write(f"{idx+1}. {cart_item['item']} - **Rp {cart_item['harga']:,}**")
                total_harga += cart_item['harga']
            
            st.markdown("---")
            st.markdown(f"### **Total Bayar: Rp {total_harga:,}**")
            
            # Form Pembayaran
            metode = st.selectbox("Pilih Metode Pembayaran:", [
                "Tunai (Cash)",
                "DANA",
                "ShopeePay",
                "OVO",
                "GoPay",
                "QRIS All Payment"
            ])
            
            nama_pelanggan = st.text_input("Nama Pelanggan:", "Nabil")
            
            if metode == "Tunai (Cash)":
                nominal_cash = st.number_input("Nominal Uang Tunai (Rp):", min_value=total_harga, value=total_harga, step=5000)
                kembalian = nominal_cash - total_harga
                st.write(f"Kembalian: **Rp {kembalian:,}**")
            elif metode == "QRIS All Payment":
                st.warning("📱 Silakan scan Kode QRIS di layar saat kasir memproses.")
            else:
                nomor_ewallet = st.text_input(f"Masukkan Nomor HP / Akun {metode}:", "081234567890")

            col_bayar, col_reset = st.columns(2)
            with col_bayar:
                if st.button("✅ Proses Pembayaran"):
                    with st.spinner("Memproses transaksi..."):
                        time.sleep(1)
                    st.success(f"🎉 Pembayaran Berhasil!\n\n**Pelanggan:** {nama_pelanggan}\n\n**Metode:** {metode}\n\n**Total:** Rp {total_harga:,}")
                    st.session_state.cart = []
            
            with col_reset:
                if st.button("🗑️ Kosongkan"):
                    st.session_state.cart = []
                    st.rerun()

# ==========================================
# 5. MENU: CATAT & REVIEW RESTO
# ==========================================
elif menu == "⭐ Catat & Review Resto":
    st.header("⭐ Review & Catat Tempat Makan Favorit")
    
    with st.form("form_review"):
        nama_tempat = st.text_input("Nama Tempat Makan / Resto:")
        menu_fav = st.text_input("Menu Rekomendasi / Favorit:")
        rating = st.slider("Rating Rasa (1 - 5 Bintang):", 1, 5, 5)
        catatan_rasa = st.text_area("Review Singkat Rasa & Suasana:")
        
        submit_review = st.form_submit_button("Simpan Review")
        if submit_review:
            if nama_tempat and menu_fav:
                st.success(f"Berhasil! Review untuk **{nama_tempat}** (Menu: *{menu_fav}*) dengan Rating ⭐ {rating}/5 telah disimpan.")
            else:
                st.warning("Nama tempat dan menu wajib diisi dulu ya!")

# Footer
st.markdown("---")
st.markdown("🚀 Dibuat menggunakan **Python (Streamlit)** | D4 Manajemen Informatika UNESA")