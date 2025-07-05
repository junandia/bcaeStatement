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
            tables = read_pdf(temp_pdf_path, pages='all', multiple_tables=True, lattice=True)
        except Exception as e:
            st.error(f"Gagal membaca PDF dengan tabula: {e}")
            st.stop()

        # Gabungkan semua tabel yang berhasil dibaca
        df_all = pd.concat(tables, ignore_index=True)
        # Pilih kolom yang relevan saja (pastikan ejaan kolom sesuai hasil ekstraksi)
        expected_columns = ["TANGGAL", "TRANSAKSI", "KELUAR (IDR)", "MASUK (IDR)", "SALDO AKHIR (IDR)"]
        actual_columns = {col.strip().upper(): col for col in df_all.columns}
        selected_columns = [actual_columns[col] for col in expected_columns if col in actual_columns]    
        if not selected_columns:
            st.warning("Tidak ada kolom yang cocok ditemukan dalam file PDF.")
            st.stop()

        df_filtered = df_all[selected_columns]
        df_filtered.columns = [col for col in expected_columns if col in actual_columns]  # rename agar rapi

        # Tampilkan hasil awal
        st.subheader("Hasil Ekstraksi Awal")
        st.dataframe(df_filtered)
        
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "transaksi_seabank.csv", "text/csv")


if __name__ == "__main__":
    mainSeaBankEstatement()
