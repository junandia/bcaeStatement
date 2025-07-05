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

    # Normalisasi nama kolom dan buang spasi
    df_all.columns = [col.strip().upper() for col in df_all.columns]

    # Mapping kolom untuk menjaga konsistensi
    expected_columns = ["TANGGAL", "TRANSAKSI", "KELUAR (IDR)", "MASUK (IDR)", "SALDO AKHIR (IDR)"]
    available_columns = [col for col in expected_columns if col in df_all.columns]

    if not available_columns:
        st.warning("Tidak ada kolom yang cocok ditemukan dalam file PDF.")
        st.stop()

    df_filtered = df_all[available_columns]
    df_filtered.columns = available_columns  # pastikan urutannya sesuai

    # Hapus baris yang seluruh selnya kosong
    df_filtered = df_filtered.dropna(how='all')

    # Tampilkan hasil akhir
    st.subheader("Data Transaksi yang Difilter")
    st.dataframe(df_filtered)
        
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "transaksi_seabank.csv", "text/csv")


if __name__ == "__main__":
    mainSeaBankEstatement()
