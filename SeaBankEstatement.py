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
        # Normalisasi nama kolom agar lebih toleran terhadap variasi hasil OCR/tabula
        def normalize_col(col):
            return col.strip().upper().replace('SALDO', 'SALDO').replace('TGL', 'TANGGAL').replace('TANGGAL', 'TANGGAL').replace('AKHIR', 'AKHIR').replace('TRANSAKSI', 'TRANSAKSI').replace('KELUAR', 'KELUAR').replace('MASUK', 'MASUK')
        normalized_columns = {normalize_col(col): col for col in df_all.columns}
        expected_columns = ["TANGGAL", "TRANSAKSI", "KELUAR (IDR)", "MASUK (IDR)", "SALDO AKHIR (IDR)"]
        # Cari kolom yang paling mirip dengan expected_columns
        selected_columns = []
        for exp_col in expected_columns:
            found = None
            for norm, orig in normalized_columns.items():
                if exp_col in norm or norm in exp_col:
                    found = orig
                    break
            if found:
                selected_columns.append(found)
        if not selected_columns or len(selected_columns) < 2:
            st.warning("Tidak ada kolom yang cocok ditemukan dalam file PDF. Cek hasil ekstraksi awal di bawah.")
            st.dataframe(df_all)
            st.stop()

        df_filtered = df_all[selected_columns]
        df_filtered.columns = [col for col in expected_columns if any(col in normalize_col(c) or normalize_col(c) in col for c in df_all.columns)]  # rename agar rapi
        # Menghapus baris yang tidak relevan
        df_filtered = df_filtered.dropna(how='all').reset_index(drop=True)
        # Menghapus baris yang hanya berisi spasi
        df_filtered = df_filtered[~df_filtered.apply(lambda x: x.astype(str).str.strip().eq('').all(), axis=1)]
        # Tampilkan hasil awal
        st.subheader("Hasil Ekstraksi Awal")
        st.dataframe(df_filtered)
        
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "transaksi_seabank.csv", "text/csv")


if __name__ == "__main__":
    mainSeaBankEstatement()
