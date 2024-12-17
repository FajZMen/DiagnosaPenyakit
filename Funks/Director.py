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
        

def proses_diagnosa(gejala_pasien, gejala_fisik_pasien, faktor_pendukung_pasien, dataset_gejala):
    penyakit_kemungkinan = "Tidak Diketahui"
    persentase_kemungkinan = 0
    resep_obat = []

    # Loop untuk mencocokkan gejala dengan dataset_gejala
    for penyakit, data in dataset_gejala.items():
        gejala_terkait = data["gejala"]
        gejala_fisik_terkait = data.get("gejalaFisik", [])
        faktor_pendukung_terkait = data.get("faktorPendukung", [])

        # Memastikan hanya gejala yang ada dalam dataset yang dihitung
        valid_gejala_pasien = [gejala for gejala in gejala_pasien if gejala in gejala_terkait]
        valid_gejala_fisik_pasien = [gejala for gejala in gejala_fisik_pasien if gejala in gejala_fisik_terkait]
        valid_faktor_pendukung_pasien = [faktor for faktor in faktor_pendukung_pasien if faktor in faktor_pendukung_terkait]

        # Hitung kecocokan untuk gejala yang ada
        match_count_gejala = len(valid_gejala_pasien)
        match_count_fisik = len(valid_gejala_fisik_pasien)
        match_count_faktor = len(valid_faktor_pendukung_pasien)

        # Total gejala yang benar
        total_gejala_benar = match_count_gejala + match_count_fisik + match_count_faktor

        # Total inputan gejala pasien (baik yang benar maupun salah)
        total_inputan_gejala = len(gejala_pasien) + len(gejala_fisik_pasien) + len(faktor_pendukung_pasien)

        # Hitung persentase kecocokan
        persentase = (total_gejala_benar / total_inputan_gejala) * 100

        # Update kemungkinan penyakit jika persentase lebih tinggi
        if persentase > persentase_kemungkinan:
            penyakit_kemungkinan = penyakit
            persentase_kemungkinan = persentase
            resep_obat = data.get("resepObat", [])


    return penyakit_kemungkinan, persentase_kemungkinan, resep_obat

def diagnosa_page():
    st.title("Halaman Diagnosa Pasien")
    st.write("Silakan masukkan data pasien untuk melakukan diagnosa.")

    # Input data pasien
    nama_pasien = st.text_input("Nama Pasien", "")
    gejala = st.text_input("Gejala Pasien (dipisahkan dengan koma)", "")
    gejala_fisik = st.text_input("Gejala Fisik Pasien (dipisahkan dengan koma)", "")
    faktor_pendukung = st.text_input("Faktor Pendukung (dipisahkan dengan koma)", "")

    # Tombol Diagnosa
    if st.button("Proses Diagnosa"):
        if nama_pasien and gejala:
            # Proses data inputan
            list_gejala = [g.strip() for g in gejala.split(",")]
            list_gejala_fisik = [gf.strip() for gf in gejala_fisik.split(",")]
            list_faktor_pendukung = [fp.strip() for fp in faktor_pendukung.split(",")]

            # Lakukan proses diagnosa
            penyakit, persentase, saran_obat = proses_diagnosa(
                list_gejala, list_gejala_fisik, list_faktor_pendukung, gejalaUmum
            )

            st.success(f"Hasil diagnosa telah disimpan ke History")

            # Simpan hasil diagnosa ke dalam history
            history_konsultasi.append({
                "nama_pasien": nama_pasien,
                "gejala": list_gejala,
                "gejala_fisik": list_gejala_fisik,
                "faktor_pendukung": list_faktor_pendukung,
                "penyakit_kemungkinan": penyakit,
                "persentase_kemungkinan": persentase,
                "saran_obat": ", ".join(saran_obat),
                "tanggal_konsultasi": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # Tampilkan hasil diagnosa
            st.subheader("Hasil Diagnosa")
            st.write(f"**Nama Pasien**: {nama_pasien}")
            st.write(f"**Gejala**: {', '.join(list_gejala)}")
            st.write(f"**Gejala Fisik**: {', '.join(list_gejala_fisik)}")
            st.write(f"**Faktor Pendukung**: {', '.join(list_faktor_pendukung)}")
            st.write(f"**Penyakit Kemungkinan**: {penyakit}")
            st.write(f"**Persentase Kemungkinan**: {persentase:.2f}%")
            st.write(f"**Saran Obat**: {', '.join(saran_obat)}")

            lanjut = st.radio("Apakah ingin melanjutkan konsultasi untuk pasien berikutnya?", ("Pilih","Ya", "Tidak"))

            if lanjut == "Ya":
                st.rerun()  
            elif lanjut == 'tidak':
                st.success("Data konsultasi telah disimpan. Anda sekarang keluar dari proses konsultasi.")
            else:
                st.error("Pilihan Tidak sesuai")

        else:
            st.error("Nama pasien dan gejala wajib diisi!")

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
