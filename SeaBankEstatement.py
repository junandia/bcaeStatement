from tabula import read_pdf
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from openpyxl import load_workbook
import streamlit as st


def extract_seabank_transactions(pdf_path):
    # Extract all tables from the PDF
    tables = read_pdf(pdf_path, pages="all", multiple_tables=True, lattice=True)
    # Find the table with the header containing 'TABUNGAN - RINCIAN TRANSAKSI'
    for table in tables:
        if table is not None and any(
            table.columns.astype(str).str.contains("TABUNGAN - RINCIAN TRANSAKSI", case=False, na=False)
        ):
            return table
    # If not found, try to find by checking the first row
    for table in tables:
        if table is not None and not table.empty and any(table.iloc[0].astype(str).str.contains("TABUNGAN - RINCIAN TRANSAKSI", case=False, na=False)):
            # Set first row as header
            table.columns = table.iloc[0]
            return table[1:]
    return pd.DataFrame()  # Return empty if not found


def mainSeaBankEstatement():
    st.title("SeaBank e-Statement Converter")

    # File uploader
    uploaded_files = st.file_uploader("Upload PDF Statements", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        all_transactions = []

        for uploaded_file in uploaded_files:
            file_path = f"temp_{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            # Extract transactions from the PDF
            df = extract_seabank_transactions(file_path)
            if not df.empty:
                all_transactions.append(df)
            else:
                st.warning(f"No transaction table found in {uploaded_file.name}")

        if all_transactions:
            # Combine all transactions
            global_dataframe = pd.concat(all_transactions, ignore_index=True)

            # Display the dataframe
            st.write("### Combined Transactions")
            st.dataframe(global_dataframe)

            # Download button
            output_filename = "Combined_Statements.xlsx"
            with pd.ExcelWriter(output_filename, engine="openpyxl") as writer:
                global_dataframe.to_excel(writer, sheet_name="All Transactions", index=False)

            with open(output_filename, "rb") as f:
                st.download_button(
                    label="Download Excel File",
                    data=f,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("No transaction data extracted from any file.")

if __name__ == "__main__":
    mainSeaBankEstatement()
