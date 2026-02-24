import PyPDF2
import pandas as pd
import re
import streamlit as st
import io
import os

# 1. Pastikan Page Config adalah perintah pertama
st.set_page_config(page_title="Mandiri Converter Pro", layout="wide")

def extract_mandiri_estatement(pdf_path):
    extracted_data = []
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        table_started = False
        
        for page in reader.pages:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Melewati header sampai ketemu tabel transaksi
                if "Posting Date" in line and "Remark" in line:
                    table_started = True
                    i += 1
                    continue
                
                if not table_started:
                    i += 1
                    continue

                # 1. DETEKSI TANGGAL (Contoh: 01 Feb 2026,)
                if re.match(r'^\d{2} \w{3} \d{4},', line):
                    date_part = line.replace(',', '').strip()
                    full_date = date_part
                    remark_parts = []
                    
                    # 2. DETEKSI JAM (Baris tepat di bawah tanggal)
                    i += 1
                    if i < len(lines):
                        next_line = lines[i].strip()
                        # Pola jam HH:mm:ss
                        time_match = re.match(r'^(\d{2}:\d{2}:\d{2})(.*)', next_line)
                        if time_match:
                            full_date = f"{date_part} {time_match.group(1)}"
                            # Sisa teks setelah jam
                            if time_match.group(2).strip():
                                remark_parts.append(time_match.group(2).strip())
                        else:
                            remark_parts.append(next_line)
                    
                    # 3. KUMPULKAN REMARK SAMPAI KETEMU BARIS NOMINAL (Greedy)
                    j = i + 1
                    debit = credit = balance = 0.0
                    found_money = False
                    
                    while j < len(lines):
                        curr_line = lines[j].strip()
                        
                        # Berhenti jika bertemu transaksi baru (failsafe)
                        if re.match(r'^\d{2} \w{3} \d{4},', curr_line):
                            break
                            
                        # Cari baris yang mengandung minimal 3 angka desimal (Debit, Credit, Balance)
                        num_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d{2}))'
                        all_nums = re.findall(num_pattern, curr_line)
                        
                        if len(all_nums) >= 3:
                            debit = float(all_nums[-3].replace(',', ''))
                            credit = float(all_nums[-2].replace(',', ''))
                            balance = float(all_nums[-1].replace(',', ''))
                            
                            # Ambil teks sebelum angka pertama (sisa Remark/Ref No)
                            text_before_nums = re.split(num_pattern, curr_line)[0].strip()
                            if text_before_nums and text_before_nums != "-":
                                remark_parts.append(text_before_nums)
                            
                            found_money = True
                            j += 1
                            break
                        else:
                            # Masukkan ke remark jika bukan footer
                            if curr_line and not any(x in curr_line for x in ["Page", "Created", "Account Statement"]):
                                remark_parts.append(curr_line)
                        j += 1
                    
                    # 4. GABUNGKAN REMARK
                    final_remark = " ".join(remark_parts).strip()
                    final_remark = re.sub(' +', ' ', final_remark) # Bersihkan spasi ganda
                    
                    if found_money:
                        extracted_data.append([
                            full_date, final_remark, debit, credit, balance
                        ])
                    
                    i = j - 1
                i += 1
                    
    df = pd.DataFrame(extracted_data, columns=["Posting Date", "Remark", "Debit", "Credit", "Balance"])
    return df

def mainMandiriEstatement():
    st.title("🏦 Mandiri e-Statement Converter (Final Fix)")
    st.markdown("Pemisahan Jam, Full Remark, dan Perbaikan Tombol Excel.")

    uploaded_files = st.file_uploader("Upload PDF Mandiri", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        all_transactions = []
        for uploaded_file in uploaded_files:
            file_path = f"temp_{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            try:
                st.write(f"🔍 Memproses: **{uploaded_file.name}**")
                df = extract_mandiri_estatement(file_path)
                if not df.empty:
                    df['source_file'] = uploaded_file.name
                    all_transactions.append(df)
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)

        if all_transactions:
            global_dataframe = pd.concat(all_transactions, ignore_index=True)
            st.write("### Preview Transaksi")
            st.dataframe(global_dataframe, use_container_width=True)

            # --- BAGIAN EXPORT MENIRU SCRIPT BCA ---
            output_filename = "Mandiri_Statement_Combined.xlsx"
            
            # Tulis ke file fisik sementara
            with pd.ExcelWriter(output_filename, engine="openpyxl") as writer:
                global_dataframe.to_excel(writer, sheet_name="All Transactions", index=False)

            # Baca kembali file tersebut untuk diunduh
            with open(output_filename, "rb") as f:
                st.download_button(
                    label="📥 Download Excel File",
                    data=f,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # Opsional: Download CSV tetap tersedia
            st.download_button("📥 Download CSV", global_dataframe.to_csv(index=False), "mandiri.csv", "text/csv")

if __name__ == "__main__":
    mainMandiriEstatement()
