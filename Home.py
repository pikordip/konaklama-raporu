import streamlit as st

st.set_page_config(page_title="Ana Sayfa", layout="wide")

st.title("🏠 Ana Sayfa - Konaklama Raporları")

st.markdown("""
Bu uygulamada aşağıdaki raporları kullanabilirsiniz:

- **Giriş Ayına Göre Rapor**: Misafirlerin giriş yaptıkları aylara göre konaklama analizleri.
- **Alış Ayına Göre Rapor**: Otel alış tarihine göre finansal ve konaklama verileri analizi.

Lütfen soldaki menüden istediğiniz raporu seçin ya da aşağıdaki butonlarla hızlıca yönlendirin.
""")

col1, col2 = st.columns(2)

with col1:
    if st.button("📅 Giriş Ayına Göre Rapor"):
        st.experimental_set_query_params(page="GirisAyinaGore")  # Bu satırı aşağıdakiyle değiştir

with col2:
    if st.button("📊 Alış Ayına Göre Rapor"):
        st.experimental_set_query_params(page="AlisAyinaGore")   # Bu satırı aşağıdakiyle değiştir

# Yeni kullanım (2024 sonrası için):
# Replace above 2 satırı aşağıdaki gibi yap

params = st.experimental_get_query_params()

if st.session_state.get("clicked_giris", False):
    st.experimental_set_query_params(page="GirisAyinaGore")

if st.session_state.get("clicked_alis", False):
    st.experimental_set_query_params(page="AlisAyinaGore")
