import streamlit as st

st.title("🏠 Ana Sayfa")

if st.button("Giriş Ayına Göre Rapor"):
    st.experimental_set_query_params(page="GirisAyinaGore")

if st.button("Alış Ayına Göre Rapor"):
    st.experimental_set_query_params(page="AlisAyinaGore")

st.markdown("Soldaki menüyü kullanarak sayfalar arasında geçiş yapabilirsiniz.")
