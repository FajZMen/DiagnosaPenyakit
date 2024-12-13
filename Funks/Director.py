import streamlit as st
import pandas as pd
import os
from io import BytesIO
from Datas.Data import gejalaUmum, gejalaGigi, dataDokter
import datetime

# History konsultasi (akan disimpan ke Excel)
history_konsultasi = []

def auth_dokter(df_dokter, id_dr):
    # Cari dokter berdasarkan ID
    dokter = df_dokter[df_dokter['id_dr'] == id_dr]

    # Jika ID tidak ditemukan
    if dokter.empty:
        return None

    # Jika ditemukan, kembalikan data dokter
    return {
        'nama': dokter.iloc[0]['name'],
        'poli': dokter.iloc[0]['poli']
    }
        
def auth_page():
    st.title("Login Dokter")
    
    id_dokter = st.text_input("Masukkan ID Dokter", value="")

    if st.button("Login"):
        df_dokter = pd.DataFrame(dataDokter)

        try:
            id_dokter = int(id_dokter)
        except ValueError:
            st.error("ID Dokter harus berupa angka!")
            return

        result = auth_dokter(df_dokter, id_dokter)

        if result:
            st.success(f"Selamat datang, Dr. {result['nama']} di poli {result['poli']}!")
            st.session_state["is_logged_in"] = True
            st.session_state["dokter"] = result
            
            st.rerun()
        else:
            st.error("ID Dokter tidak ditemukan.")
        
def proses_diagnosa(gejala_pasien, dataset_gejala):
    penyakit_kemungkinan = "Tidak Diketahui"
    persentase_kemungkinan = 0

    # Loop untuk mencocokkan gejala dengan dataset_gejala
    for penyakit, data in dataset_gejala.items():
        gejala_terkait = data["gejala"]
        match_count = len(set(gejala_pasien) & set(gejala_terkait))
        total_gejala = len(gejala_terkait)
        persentase = (match_count / total_gejala) * 100

        if persentase > persentase_kemungkinan:
            penyakit_kemungkinan = penyakit
            persentase_kemungkinan = persentase

    return penyakit_kemungkinan, persentase_kemungkinan

def diagnosa_page():
    if not st.session_state.get("is_logged_in", False):
        st.warning("Silakan login terlebih dahulu.")
        return

    st.title(f"Diagnosa Pasien")
    nama_pasien = st.text_input("Masukkan Nama Pasien")
    poli_dokter = st.session_state["dokter"]["poli"]

    # Menampilkan input gejala sebagai teks
    gejala_input = st.text_area("Masukkan Gejala Pasien (dipisahkan dengan koma)", "")

    if st.button("Diagnosa"):
        if gejala_input:
            # Mengubah input gejala yang dipisahkan koma menjadi list
            gejala = [gejala.strip() for gejala in gejala_input.split(",")]

            # Proses diagnosa berdasarkan poli yang dipilih
            if poli_dokter == "Poli Umum":
                penyakit, persentase = proses_diagnosa(gejala, gejalaUmum)
            elif poli_dokter == "Poli Gigi":
                penyakit, persentase = proses_diagnosa(gejala, gejalaGigi)

            # Menampilkan hasil diagnosa
            st.write(f"**Penyakit yang kemungkinan diderita:** {penyakit}")
            st.write(f"**Persentase Kemungkinan:** {persentase:.2f}%")

            # Simpan hasil diagnosa ke history konsultasi
            history_konsultasi.append({
                "nama_pasien": nama_pasien,
                "gejala": gejala,
                "penyakit_kemungkinan": penyakit,
                "persentase_kemungkinan": persentase,
                "dokter": st.session_state["dokter"]["nama"],  # Nama dokter dari session
                "poli": poli_dokter,
                "tanggal_konsultasi": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            st.success(f"Hasil diagnosa telah disimpan ke History Konsultasi.")

            lanjut = st.radio("Apakah ingin melanjutkan konsultasi untuk pasien berikutnya?", ("Pilih","Ya", "Tidak"))

            if lanjut == "Ya":
                st.rerun()  
            elif lanjut == 'tidak':
                st.success("Data konsultasi telah disimpan. Anda sekarang keluar dari proses konsultasi.")
            else:
                st.error("Pilihan Tidak sesuai")
                
        else:
            st.error("Silakan masukkan gejala terlebih dahulu.")

def downloadhistory():
    if history_konsultasi:
        historyfile = BytesIO()
        pd.DataFrame(history_konsultasi).to_excel(historyfile, index=False)
        historyfile.seek(0)

        st.download_button(
            label = "Download List Pesanan",
            data = historyfile.getvalue(),
            file_name = "HistoryKonsultasi.xlsx",
            mime = "application/vnd.ms-excel"
        )

def history_page():
    st.title("History Konsultasi")
    if history_konsultasi:
        st.dataframe(history_konsultasi)
        downloadhistory()
    else:
        st.write("Belum ada riwayat konsultasi, Mohon untuk melakukan konsultasi sekali.")

def gejala_page():
    selectpoli = st.selectbox(
        "Lihat Gejala",
        ("Poli Umum", "Poli Gigi"),
        index=None,
        placeholder="Pilih Poli Gejala",
    )
    if selectpoli == "Poli Umum":
        st.dataframe(gejalaUmum)
    elif selectpoli == "Poli Gigi":
        st.dataframe(gejalaGigi)