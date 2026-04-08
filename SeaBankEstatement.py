import streamlit as st
import pandas as pd
import pdfplumber
import tempfile
import os
import re

# =========================
# CONFIG
# =========================
MONTHS = ["JAN","FEB","MAR","APR","MEI","JUN","JUL","AGU","SEP","OKT","NOV","DES"]

# =========================
# HELPERS
# =========================
def clean_number(x):
    if not x:
        return 0.0
    x = str(x).replace(".", "").replace(",", ".")
    try:
        return float(x)
    except:
        return 0.0


def is_date_line(line):
    return re.match(rf"^\d{{1,2}}\s+({'|'.join(MONTHS)})", line.upper())


def extract_numbers(text):
    return re.findall(r"\d{1,3}(?:\.\d{3})*(?:,\d{2})?", text)


def is_header_row(row):
    joined = " ".join([str(c).upper() for c in row if c])
    return any(x in joined for x in ["TANGGAL", "TRANSAKSI", "KELUAR", "MASUK", "SALDO"])


# =========================
# TABLE PARSER
# =========================
def parse_table(pdf_path, year):
    results = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if not table:
                    continue

                for row in table:
                    if not row or len(row) < 5:
                        continue

                    if is_header_row(row):
                        continue

                    tanggal = str(row[0]).strip()
                    if not is_date_line(tanggal):
                        continue

                    transaksi = str(row[1]).strip()
                    keluar = row[2]
                    masuk = row[3]
                    saldo = row[4]

                    results.append({
                        "Tanggal": f"{tanggal} {year}",
                        "Keterangan": transaksi,
                        "Debit": clean_number(keluar),
                        "Credit": clean_number(masuk),
                        "Saldo": clean_number(saldo)
                    })

    return results


# =========================
# MULTILINE PARSER (FALLBACK)
# =========================
def parse_multiline(pdf_path, year):
    results = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")
            i = 0

            while i < len(lines):
                line = lines[i].strip()

                if is_date_line(line):
                    tanggal = line
                    i += 1

                    transaksi_lines = []
                    keluar = ""
                    masuk = ""
                    saldo = ""

                    while i < len(lines):
                        current = lines[i].strip()

                        if is_date_line(current):
                            break

                        numbers = extract_numbers(current)

                        if numbers:
                            if len(numbers) >= 3:
                                keluar = numbers[-3]
                                masuk = numbers[-2]
                                saldo = numbers[-1]
                            elif len(numbers) == 2:
                                keluar = numbers[-2]
                                saldo = numbers[-1]
                            elif len(numbers) == 1:
                                saldo = numbers[0]
                        else:
                            transaksi_lines.append(current)

                        i += 1

                    if transaksi_lines:
                        results.append({
                            "Tanggal": f"{tanggal} {year}",
                            "Keterangan": " ".join(transaksi_lines),
                            "Debit": clean_number(keluar),
                            "Credit": clean_number(masuk),
                            "Saldo": clean_number(saldo)
                        })

                else:
                    i += 1

    return results


# =========================
# MERGE + CLEAN
# =========================
def merge_results(table_data, text_data):
    df1 = pd.DataFrame(table_data)
    df2 = pd.DataFrame(text_data)

    df = pd.concat([df1, df2], ignore_index=True)

    # Remove duplikat berdasarkan kombinasi unik
    df = df.drop_duplicates(subset=["Tanggal", "Keterangan", "Saldo"])

    # Sort by tanggal (opsional)
    df = df.reset_index(drop=True)

    return df


# =========================
# MAIN APP
# =========================
def mainSeaBankEstatement():
    st.title("🏦 SeaBank Hybrid Parser (Production Ready)")

    uploaded_file = st.file_uploader("Upload PDF Rekening Koran", type=["pdf"])

    year = st.number_input("Tahun", value=2026)

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = tmp.name

        try:
            st.info("⏳ Parsing data...")

            table_data = parse_table(pdf_path, year)
            multiline_data = parse_multiline(pdf_path, year)

            df = merge_results(table_data, multiline_data)

            if df.empty:
                st.error("❌ Tidak ada data ditemukan")
                return

            st.success(f"✅ {len(df)} transaksi berhasil diekstrak")

            st.dataframe(df, use_container_width=True)

            # =========================
            # SUMMARY
            # =========================
            st.subheader("📊 Ringkasan")

            total_debit = df["Debit"].sum()
            total_credit = df["Credit"].sum()

            col1, col2 = st.columns(2)
            col1.metric("Total Debit", f"{total_debit:,.2f}")
            col2.metric("Total Credit", f"{total_credit:,.2f}")

            # =========================
            # DOWNLOAD
            # =========================
            csv = df.to_csv(index=False)
            st.download_button("⬇️ Download CSV", csv, "seabank.csv")

            excel_path = pdf_path.replace(".pdf", ".xlsx")
            df.to_excel(excel_path, index=False)

            with open(excel_path, "rb") as f:
                st.download_button("⬇️ Download Excel", f, "seabank.xlsx")

        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)


if __name__ == "__main__":
    mainSeaBankEstatement()
