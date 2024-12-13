import os
import pandas as pd 

file_path = os.path.join(os.path.dirname(__file__), "dataRumahSakit98.xlsx")

df_dokter = pd.read_excel(file_path, sheet_name="Dokter")
dataDokter = df_dokter.to_dict(orient="records")

df_gejala_umum = pd.read_excel(file_path, sheet_name="GejalaUmum")
gejalaUmum = {
    row['penyakit']: {
        'gejala': row['gejala'].split(','),
        'gejalaFisik': row['gejalaFisik'].split(',') if pd.notna(row['gejalaFisik']) else [],
        'faktorPendukung': row['faktorPendukung'].split(',') if pd.notna(row['faktorPendukung']) else [],
        'resepObat': row['resepObat'].split(',') if pd.notna(row['resepObat']) else []
    }
    for _, row in df_gejala_umum.iterrows()
}

df_gejala_gigi = pd.read_excel(file_path, sheet_name="GejalaGigi")
gejalaGigi = {
    row['penyakit']: {'gejala': row['gejala'].split(',')}
    for _, row in df_gejala_gigi.iterrows()
}

__all__ = ['dataDokter', 'gejalaUmum', 'gejalaGigi']