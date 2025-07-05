import streamlit as st
import pandas as pd
from io import BytesIO
import io

from BcaEstatement import mainBcaEstatement
from SeaBankEstatement import mainSeaBankEstatement
from MandiriEstatement import mainMandiriEstatement
from BsiEstatement import mainBsiEstatement

def main():
    st.title("Aplikasi Statement Bank Konverter PDF to Excel")
    st.markdown("Aplikasi ini digunakan untuk mengkonversi file statement bank dari format PDF ke format Excel.")

    # Sidebar dengan menu pilihan
    st.sidebar.title('Menu')
    menu = st.sidebar.selectbox('Pilih Menu', ["Beranda", "BCA", "SeaBank","Mandiri","BSI"])

    # Pilihan menu
    if menu == "BCA":
        st.subheader("Konversi BCA e-Statement ke Excel")
        mainBcaEstatement()
    elif menu == "SeaBank":
        st.subheader("Konversi SeaBank e-Statement ke Excel")
        mainSeaBankEstatement()
    elif menu == "Mandiri":
        st.subheader("Konversi Mandiri e-Statement ke Excel")
        st.write("Fitur ini masih dalam pengembangan.")
        mainMandiriEstatement()
    elif menu == "BSI":
        st.subheader("Konversi BSI e-Statement ke Excel")
        st.write("Fitur ini masih dalam pengembangan.")
        mainBsiEstatement()
    else:
        st.subheader("Selamat datang di aplikasi konversi statement bank!")
        st.write("Silakan pilih menu di sidebar untuk memulai.")


# Memanggil fungsi utama
if __name__ == "__main__":
    main()
