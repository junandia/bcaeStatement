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
            c = col.strip().upper()
            c = c.replace('TGL', 'TANGGAL')
            c = c.replace('TANGGAL', 'TANGGAL')
            c = c.replace('SALDO', 'SALDO')
            c = c.replace('AKHIR', 'AKHIR')
            c = c.replace('TRANSAKSI', 'TRANSAKSI')
            c = c.replace('KELUAR', 'KELUAR')
            c = c.replace('MASUK', 'MASUK')
            c = c.replace('DEBET', 'KELUAR')
            c = c.replace('KREDIT', 'MASUK')
            c = c.replace('IDR', '')
            c = c.replace('  ', ' ')
            return c.strip()
        # Hilangkan duplikat kolom setelah normalisasi
        normalized_columns = {}
        for col in df_all.columns:
            norm = normalize_col(col)
            if norm not in normalized_columns:
                normalized_columns[norm] = col
        expected_columns = ["TANGGAL", "TRANSAKSI", "KELUAR", "MASUK", "SALDO AKHIR"]
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
        # Rename kolom agar rapi dan konsisten
        rename_map = {}
        for i, col in enumerate(df_filtered.columns):
            if i < len(expected_columns):
                rename_map[col] = expected_columns[i] + (" (IDR)" if expected_columns[i] in ["KELUAR", "MASUK", "SALDO AKHIR"] else "")
        df_filtered = df_filtered.rename(columns=rename_map)
        # Menghapus baris yang tidak relevan
        df_filtered = df_filtered.dropna(how='all').reset_index(drop=True)
        # Tampilkan hasil awal
        st.subheader("Hasil Ekstraksi Awal")
        st.dataframe(df_filtered)
        
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "transaksi_seabank.csv", "text/csv")


if __name__ == "__main__":
    mainSeaBankEstatement()
