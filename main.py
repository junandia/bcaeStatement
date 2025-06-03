import streamlit as st
import pandas as pd
from io import BytesIO
import io

from BcaEstatement import mainBcaEstatement

def main():
    st.title("Aplikasi Statement Bank Konverter PDF to Excel")
    st.markdown("Aplikasi ini digunakan untuk mengkonversi file statement bank dari format PDF ke format Excel.")

    # Sidebar dengan menu pilihan
    st.sidebar.title('Menu')
    menu = st.sidebar.selectbox('Pilih Menu', ["Beranda", "Bank BCA e-Statement"])

    # Pilihan menu
    if menu == "Bank BCA e-Statement":
        st.subheader("Konversi BCA e-Statement ke Excel")
        mainBcaEstatement()


# Memanggil fungsi utama
if __name__ == "__main__":
    main()
