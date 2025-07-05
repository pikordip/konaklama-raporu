import streamlit as st

st.set_page_config(page_title="Ana Sayfa", layout="wide")

st.title("🏠 Ana Sayfa - Konaklama Raporları")

st.markdown("""
Bu uygulamada **Kişi Başı Geceleme Tutarları** üzerine iki farklı rapor sunulmaktadır:

- **Giriş Ayına Göre Rapor:** Misafirlerin giriş yaptıkları aya göre kişi başı geceleme tutarlarını analiz eder.
- **Alış Ayına Göre Rapor:** Otel alış tarihine göre kişi başı geceleme tutarlarını gösterir.

Lütfen sol menüden ilgili raporu seçerek devam edin.
""")
