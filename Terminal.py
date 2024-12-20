import streamlit as st

st.set_page_config(page_title="Klinik Bidan Ani", page_icon="🏥")

st.title("Sistem Konsultasi Klinik Bidan Ani")
st.image("images/cover.png", caption="14230, Jl. Alur Laut I No.9 2, RT.2/RW.3, Rawabadak Sel., Kec : koja, Jkt Utara, Daerah Khusus Ibukota Jakarta 14230")

is_logged_in = st.session_state.get("is_logged_in", False)

if not is_logged_in:
    st.sidebar.title("Navigasi")
else:
    st.sidebar.title(st.session_state.get('dokter', {}).get('nama', 'Dokter'))

if not is_logged_in:
    page = st.sidebar.radio(
        "Pilih Halaman",
        ["Landing Page", "Login Dokter"]
    )
else:
    page = st.sidebar.radio(
        "Pilih Halaman",
        ["Diagnosa", "Lihat Gejala", "Riwayat Konsultasi"]
    )

# Konten setiap halaman
if page == "Landing Page":
    st.write("Selamat datang di Klinik Bidan Ani!")
    st.write("Silakan gunakan menu navigasi di samping untuk masuk ke halaman yang diinginkan.")
elif page == "Login Dokter":
    from Funks.Director import auth_page
    auth_page()
elif page == "Dashboard":
    st.write(f"Selamat datang, {st.session_state.get('dokter', {}).get('nama', 'Dokter')}!")
    st.write("Gunakan menu di samping untuk mengakses fitur yang tersedia.")
elif page == "Diagnosa":
    from Funks.Director import diagnosa_page
    diagnosa_page()
elif page == "Lihat Gejala":
    from Funks.Director import gejala_page
    gejala_page()
elif page == "Riwayat Konsultasi":
    from Funks.Director import history_page
    history_page()
else:
    st.write("Halaman tidak ditemukan.")
