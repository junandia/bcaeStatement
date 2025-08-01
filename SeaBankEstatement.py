import streamlit as st
import pandas as pd
import pdfplumber
import os
import re

def is_date_line(line):
    return re.match(r"^\d{2} (JAN|FEB|MAR|APR|MEI|JUN|JUL|AGU|SEP|OKT|NOV|DES)", line.upper())


def mainSeaBankEstatement():
    st.title("Ekstrak Tabel 'TABUNGAN - RINCIAN TRANSAKSI' dari Rekening Koran SeaBank")

    uploaded_file = st.file_uploader("Unggah file PDF Rekening Koran", type="pdf")

    if uploaded_file:
        temp_pdf_path = "temp_seabank.pdf"
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("Mengekstrak tabel, mohon tunggu...")

        result_data = []
        with pdfplumber.open(temp_pdf_path) as pdf:
            for page in pdf.pages:
                lines = page.extract_text().split("\n")
                i = 0
                while i < len(lines):
                    if is_date_line(lines[i]):
                        tanggal = lines[i].strip()
                        transaksi = ""
                        keluar = ""
                        masuk = ""
                        saldo = ""

                        # Baca baris deskripsi berikutnya
                        i += 1
                        while i < len(lines) and not is_date_line(lines[i]):
                            transaksi += lines[i].strip() + " "
                            match = re.findall(r"\d{1,3}(?:\.\d{3})*(?:,\d{2})?", lines[i])
                            if len(match) == 3:
                                keluar, masuk, saldo = match
                            elif len(match) == 2:
                                masuk, saldo = match
                            elif len(match) == 1:
                                saldo = match[0]
                            i += 1

                        result_data.append({
                            "Tanggal": tanggal,
                            "Transaksi": transaksi.strip(),
                            "Keluar (IDR)": keluar,
                            "Masuk (IDR)": masuk,
                            "Saldo Akhir (IDR)": saldo
                        })
                    else:
                        i += 1

        if result_data:
            df_final = pd.DataFrame(result_data)
            st.success("Berhasil mengekstrak transaksi tabungan.")
            st.dataframe(df_final)
            st.download_button("Unduh sebagai CSV", df_final.to_csv(index=False), "tabungan.csv")
            st.download_button("Unduh sebagai JSON", df_final.to_json(orient="records"), "tabungan.json")
        else:
            st.warning("Tidak ditemukan data transaksi.")

        os.remove(temp_pdf_path)


if __name__ == "__main__":
    mainSeaBankEstatement()
