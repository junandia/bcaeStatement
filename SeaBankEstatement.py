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

        # Filter tabel yang memiliki header khas transaksi tabungan
        result_tables = []
        for table in tables:
            if table.shape[1] >= 4:  # Minimal kolom untuk transaksi: Tanggal, Keluar, Masuk, Saldo
                header = table.columns.str.upper().tolist()
                if any("TANGGAL" in col for col in header) and any("SALDO" in col for col in header):
                    result_tables.append(table)

        # Gabungkan hasil
        if result_tables:
            final_df = pd.concat(result_tables, ignore_index=True)

            st.success("Berhasil mengekstrak tabel TABUNGAN - RINCIAN TRANSAKSI")
            st.dataframe(final_df)

            # Unduh sebagai CSV dan JSON
            st.download_button("Unduh sebagai CSV", final_df.to_csv(index=False), "tabungan_transaksi.csv")
            st.download_button("Unduh sebagai JSON", final_df.to_json(orient="records"), "tabungan_transaksi.json")
        else:
            st.warning("Tidak ditemukan tabel dengan header 'TABUNGAN - RINCIAN TRANSAKSI'.")


if __name__ == "__main__":
    mainSeaBankEstatement()
