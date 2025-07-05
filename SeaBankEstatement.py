from tabula import read_pdf
import pandas as pd
import numpy as np
import pdfplumber
import io
import re
import os
from tqdm import tqdm
from openpyxl import load_workbook
import streamlit as st


def mainSeaBankEstatement():
    st.title("BCA e-Statement Converter")

    uploaded_file = st.file_uploader("Upload file rekening koran (PDF)", type="pdf")

    if uploaded_file is not None:
        with pdfplumber.open(uploaded_file) as pdf:
            all_text = ""
            for page in pdf.pages:
                all_text += page.extract_text() + "\n"

         # Regex untuk ekstraksi transaksi dengan deskripsi dan bulan dinamis
    pattern = re.compile(
        r"(\d{2} [A-Z]{3})\n(.*?)\n.*?(\d{1,3}(?:\.\d{3})*)?\s*(\d{1,3}(?:\.\d{3})*)?\s*(\d{1,3}(?:\.\d{3})*)",
        re.MULTILINE
    )

    transaksi = []
    for match in pattern.finditer(all_text):
        tanggal = match.group(1)
        deskripsi = match.group(2).strip()
        keluar_raw = match.group(3)
        masuk_raw = match.group(4)
        saldo_raw = match.group(5)

        keluar = int(keluar_raw.replace(".", "")) if keluar_raw else 0
        masuk = int(masuk_raw.replace(".", "")) if masuk_raw else 0
        saldo = int(saldo_raw.replace(".", "")) if saldo_raw else 0

        transaksi.append({
            "Tanggal": tanggal,
            "Transaksi": deskripsi,
            "Keluar (IDR)": keluar,
            "Masuk (IDR)": masuk,
            "Saldo Akhir (IDR)": saldo
        })


        df = pd.DataFrame(transaksi)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "transaksi_seabank.csv", "text/csv")


if __name__ == "__main__":
    mainSeaBankEstatement()
