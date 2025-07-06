from tabula import read_pdf
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from openpyxl import load_workbook
import streamlit as st
import fitz


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

        # Hitung jumlah halaman dengan PyMuPDF
        with fitz.open(temp_pdf_path) as pdf:
            page_count = len(pdf)

        result_tables = []

        for page in range(1, page_count + 1):
            page_tables = read_pdf(temp_pdf_path, pages=page, multiple_tables=True, lattice=True)
            for table in page_tables:
                if table.shape[1] >= 4:
                    headers = [str(h).strip().upper() for h in table.columns]
                    if ("TANGGAL" in headers[0] and
                        "KELUAR" in headers[1] and
                        "MASUK" in headers[2] and
                        "SALDO" in headers[3]):
                        result_tables.append(table)

        # Gabungkan hasil
        if result_tables:
            final_df = pd.concat(result_tables, ignore_index=True)

            st.success("Berhasil mengekstrak tabel transaksi tabungan berdasarkan header.")
            st.dataframe(final_df)

            # Unduh sebagai CSV dan JSON
            st.download_button("Unduh sebagai CSV", final_df.to_csv(index=False), "tabungan_transaksi.csv")
            st.download_button("Unduh sebagai JSON", final_df.to_json(orient="records"), "tabungan_transaksi.json")
        else:
            st.warning("Tidak ditemukan tabel dengan header transaksi tabungan yang sesuai.")

        # Hapus file sementara
        os.remove(temp_pdf_path)
if __name__ == "__main__":
    mainSeaBankEstatement()
