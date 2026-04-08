import streamlit as st
import pandas as pd
import pdfplumber
import tempfile
import os
import re

# =========================
# CLEANING FUNCTIONS
# =========================
def clean_number(x):
    if not x:
        return 0.0
    x = str(x).replace(".", "").replace(",", ".")
    try:
        return float(x)
    except:
        return 0.0


def is_header_row(row):
    joined = " ".join([str(c).upper() for c in row if c])
    return any(x in joined for x in ["TANGGAL", "TRANSAKSI", "KELUAR", "MASUK", "SALDO"])


def is_valid_row(row):
    if not row:
        return False
    return any(cell for cell in row)


# =========================
# CORE PARSER (TABLE BASED)
# =========================
def parse_seabank_table(pdf_path, year):
    results = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):

            tables = page.extract_tables()

            for table in tables:
                if not table:
                    continue

                for row in table:
                    if not is_valid_row(row):
                        continue

                    # Skip header
                    if is_header_row(row):
                        continue

                    # Expected structure:
                    # [Tanggal, Transaksi, Keluar, Masuk, Saldo]
                    if len(row) < 5:
                        continue

                    tanggal = str(row[0]).strip()
                    transaksi = str(row[1]).strip()
                    keluar = row[2]
                    masuk = row[3]
                    saldo = row[4]

                    # Filter hanya baris yang benar-benar transaksi
                    if not re.match(r"^\d{1,2}\s", tanggal):
                        continue

                    results.append({
                        "Tanggal": f"{tanggal} {year}",
                        "Keterangan": transaksi,
                        "Debit": clean_number(keluar),
                        "Credit": clean_number(masuk),
                        "Saldo": clean_number(saldo)
                    })

    return pd.DataFrame(results)


# =========================
# STREAMLIT APP
# =========================
def main():
    st.title("🏦 SeaBank Parser (Table-Based, High Accuracy)")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    year = st.number_input("Tahun Transaksi", min_value=2020, max_value=2030, value=2026)

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        try:
            st.info("⏳ Memproses tabel PDF...")

            df = parse_seabank_table(temp_path, year)

            if df.empty:
                st.error("❌ Tidak ada data ditemukan. Kemungkinan format PDF berbeda.")
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
            st.download_button("⬇️ CSV", csv, "seabank.csv")

            excel_path = temp_path.replace(".pdf", ".xlsx")
            df.to_excel(excel_path, index=False)

            with open(excel_path, "rb") as f:
                st.download_button("⬇️ Excel", f, "seabank.xlsx")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    main()
