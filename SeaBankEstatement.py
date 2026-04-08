import streamlit as st
import pandas as pd
import pdfplumber
import os
import re
import tempfile

# =========================
# CONFIG
# =========================
MONTHS = ["JAN","FEB","MAR","APR","MEI","JUN","JUL","AGU","SEP","OKT","NOV","DES"]

# =========================
# HELPER FUNCTIONS
# =========================
def is_date_line(line: str) -> bool:
    return re.match(rf"^\d{{1,2}}\s+({'|'.join(MONTHS)})", line.upper()) is not None


def find_table_start(lines):
    for i, line in enumerate(lines):
        if "TABUNGAN - RINCIAN TRANSAKSI" in line.upper():
            return i
    return 0


def remove_header_lines(lines):
    cleaned = []
    for line in lines:
        upper = line.upper()
        if any(x in upper for x in ["TANGGAL", "TRANSAKSI", "KELUAR", "MASUK", "SALDO"]):
            continue
        cleaned.append(line)
    return cleaned


def extract_numbers(line):
    return re.findall(r"\d{1,3}(?:\.\d{3})*(?:,\d{2})?", line)


def clean_number(x):
    if not x:
        return 0.0
    return float(x.replace(".", "").replace(",", "."))


# =========================
# CORE PARSER
# =========================
def parse_seabank_pdf(pdf_path):
    results = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            raw_text = page.extract_text()
            if not raw_text:
                continue

            lines = raw_text.split("\n")

            # --- SPECIAL HANDLING PAGE 1 ---
            if page.page_number == 1:
                start_idx = find_table_start(lines)
                lines = lines[start_idx:]

            # --- REMOVE HEADER ---
            lines = remove_header_lines(lines)

            i = 0
            while i < len(lines):
                line = lines[i]

                if is_date_line(line):
                    tanggal = line.strip()
                    transaksi = ""
                    keluar = ""
                    masuk = ""
                    saldo = ""

                    i += 1

                    while i < len(lines) and not is_date_line(lines[i]):
                        current_line = lines[i].strip()
                        transaksi += current_line + " "

                        nums = extract_numbers(current_line)

                        if len(nums) >= 3:
                            keluar = nums[-3]
                            masuk = nums[-2]
                            saldo = nums[-1]
                        elif len(nums) == 2:
                            masuk = nums[-2]
                            saldo = nums[-1]
                        elif len(nums) == 1:
                            saldo = nums[-1]

                        i += 1

                    results.append({
                        "Tanggal": tanggal,
                        "Keterangan": transaksi.strip(),
                        "Debit": clean_number(keluar),
                        "Credit": clean_number(masuk),
                        "Saldo": clean_number(saldo)
                    })

                else:
                    i += 1

    return pd.DataFrame(results)


# =========================
# STREAMLIT APP
# =========================
def mainSeaBankEstatement():
    st.title("📄 SeaBank Statement Parser (Production Ready)")

    uploaded_file = st.file_uploader("Upload PDF Rekening Koran SeaBank", type=["pdf"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        try:
            st.info("⏳ Memproses file...")

            df = parse_seabank_pdf(temp_path)

            if df.empty:
                st.warning("Tidak ditemukan data transaksi.")
                return

            st.success(f"✅ Berhasil ekstrak {len(df)} transaksi")

            st.dataframe(df, use_container_width=True)

            # =========================
            # SUMMARY
            # =========================
            total_debit = df["Debit"].sum()
            total_credit = df["Credit"].sum()

            st.subheader("📊 Ringkasan")
            col1, col2 = st.columns(2)
            col1.metric("Total Debit", f"{total_debit:,.2f}")
            col2.metric("Total Credit", f"{total_credit:,.2f}")

            # =========================
            # DOWNLOAD
            # =========================
            csv = df.to_csv(index=False)
            st.download_button("⬇️ Download CSV", csv, "seabank.csv")

            # Excel
            excel_path = temp_path.replace(".pdf", ".xlsx")
            df.to_excel(excel_path, index=False)

            with open(excel_path, "rb") as f:
                st.download_button("⬇️ Download Excel", f, "seabank.xlsx")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    mainSeaBankEstatement()
