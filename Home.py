import streamlit as st

st.set_page_config(page_title="Ana Sayfa", layout="wide")

st.title("🏠 Ana Sayfa - Konaklama Raporları")

st.markdown("""
Bu uygulamada **Kişi Başı Geceleme Tutarları** üzerine iki farklı rapor sunulmaktadır:

- **Giriş Ayına Göre Rapor:** Misafirlerin giriş yaptıkları aya göre kişi başı geceleme tutarlarını analiz eder.
- **Alış Ayına Göre Rapor:** Otel alış tarihine göre kişi başı geceleme tutarlarını gösterir.

Lütfen sol menüden ilgili raporu seçerek devam edin.
""")

import streamlit as st

st.set_page_config(page_title="Giriş", layout="centered")

# Şifreni buraya tanımla
CORRECT_PASSWORD = "seninsifren123"

# Kullanıcı daha önce giriş yaptıysa, doğrudan geçsin
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Giriş Ekranı")

    password = st.text_input("Şifreyi giriniz", type="password")

    if st.button("Giriş Yap"):
        if password == CORRECT_PASSWORD:
            st.session_state["authenticated"] = True
            st.success("Giriş başarılı. Sol menüden raporlara ulaşabilirsiniz.")
        else:
            st.error("Hatalı şifre. Lütfen tekrar deneyin.")
    st.stop()
else:
    st.success("✅ Giriş yapıldı. Raporlara erişebilirsiniz.")
