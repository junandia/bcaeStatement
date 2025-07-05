from tabula import read_pdf
import pandas as pd
import numpy as np
import io
import re
import os
from tqdm import tqdm
from openpyxl import load_workbook
import streamlit as st
import tempfile


def mainSeaBankEstatement():
    st.title("SeaBank e-Statement Converter")
    uploaded_file = st.file_uploader("Upload file rekening koran (PDF)", type="pdf")

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_pdf_path = tmp_file.name

        # Menggunakan tabula untuk mengekstrak tabel dari PDF
        try:
            tables = read_pdf(temp_pdf_path, pages='all', multiple_tables=True, lattice=True, guess=False)
        except Exception as e:
            st.error(f"Gagal membaca PDF dengan tabula: {e}")
            st.stop()

        # Gabungkan semua tabel yang berhasil dibaca
        df_all = pd.concat(tables, ignore_index=True)

         # Normalisasi nama kolom dan tampilkan sebagai referensi
        df_all.columns = [col.strip().upper() for col in df_all.columns if isinstance(col, str)]
        #st.subheader("Nama Kolom yang Terdeteksi")
        #st.write(df_all.columns.tolist())

        # Buat mapping kolom manual jika perlu
        column_mapping = {
            "UNNAMED: 0": "TANGGAL",
            "UNNAMED: 1": "SALDO AKHIR (IDR)",
            "TRANSAKSI": "TRANSAKSI",
            "KELUAR (IDR)": "KELUAR (IDR)",
            "MASUK (IDR)": "MASUK (IDR)"
        }

        df_all.rename(columns=column_mapping, inplace=True)
        # Mapping manual jika header tidak dikenali
        # Misalnya jika kolom tidak bernama, kita bisa set header secara manual:
        expected_columns = ["TANGGAL", "TRANSAKSI", "KELUAR (IDR)", "MASUK (IDR)", "SALDO AKHIR (IDR)"]
        #if len(df_all.columns) >= 5 and all(isinstance(col, str) for col in df_all.columns):
        #    df_all.columns = expected_columns[:len(df_all.columns)]

        # Ambil hanya kolom yang cocok
        available_columns = [col for col in expected_columns if col in df_all.columns]
        df_filtered = df_all[available_columns]

        # Hapus baris yang seluruh selnya kosong
        df_filtered = df_filtered.dropna(how='all')

        st.subheader("Data Transaksi yang Difilter")
        st.dataframe(df_filtered)
            
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "transaksi_seabank.csv", "text/csv")


if __name__ == "__main__":
    mainSeaBankEstatement()
