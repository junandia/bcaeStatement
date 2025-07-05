from tabula import read_pdf
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from openpyxl import load_workbook
import streamlit as st


def mainSeaBankEstatement():
    st.title("SeaBank e-Statement Converter")
    # Upload PDF file
    uploaded_file = st.file_uploader("Unggah file PDF Rekening Koran", type="pdf")

    if uploaded_file:
        # Simpan sementara file PDF
        temp_pdf_path = "temp_seabank.pdf"
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("Mengekstrak tabel, mohon tunggu...")

        # Ekstrak semua tabel dari semua halaman
        tables = read_pdf(temp_pdf_path, pages="all", multiple_tables=True, lattice=True)

# Deteksi tabel yang kemungkinan bagian dari "TABUNGAN - RINCIAN TRANSAKSI"
    # Asumsikan format tabel transaksi selalu punya minimal 4 kolom dan baris pertama adalah tanggal
    result_tables = []
    bulan_pattern = r"\d{2} (JAN|FEB|MAR|APR|MEI|JUN|JUL|AGU|SEP|OKT|NOV|DES)"

    for table in tables:
        if table.shape[1] >= 4:
            first_col = table.iloc[:, 0].astype(str).str.upper().str.strip()
            if first_col.str.contains(bulan_pattern).any():
                result_tables.append(table)

    # Gabungkan hasil
    if result_tables:
        final_df = pd.concat(result_tables, ignore_index=True)

        st.success("Berhasil mengekstrak tabel transaksi tabungan")
        st.dataframe(final_df)

        # Unduh sebagai CSV dan JSON
        st.download_button("Unduh sebagai CSV", final_df.to_csv(index=False), "tabungan_transaksi.csv")
        st.download_button("Unduh sebagai JSON", final_df.to_json(orient="records"), "tabungan_transaksi.json")
    else:
        st.warning("Tidak ditemukan tabel transaksi tabungan.")

       # Hapus file sementara
    os.remove(temp_pdf_path)
if __name__ == "__main__":
    mainSeaBankEstatement()
