import streamlit as st
import pdfplumber
import pandas as pd
import io
import re

st.title("Extract Transaksi dari Rekening Koran SeaBank")

uploaded_file = st.file_uploader("Upload file rekening koran (PDF)", type="pdf")

if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        all_text = ""
        for page in pdf.pages:
            all_text += page.extract_text() + "\n"

    # Regex untuk ekstraksi transaksi
    pattern = re.compile(r"(\d{2} JUN).*?(\d[\d\.]*|)\s+(\d[\d\.]*|)\s+(\d[\d\.]*)", re.MULTILINE)
    
    transaksi = []
    for match in pattern.finditer(all_text):
        tanggal = match.group(1)
        keluar = match.group(2).replace(".", "") if match.group(2) else "0"
        masuk = match.group(3).replace(".", "") if match.group(3) else "0"
        saldo = match.group(4).replace(".", "")
        
        transaksi.append({
            "Tanggal": tanggal,
            "Keluar (IDR)": int(keluar),
            "Masuk (IDR)": int(masuk),
            "Saldo Akhir (IDR)": int(saldo)
        })

    df = pd.DataFrame(transaksi)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "transaksi_seabank.csv", "text/csv")
