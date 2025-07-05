import streamlit as st

st.set_page_config(page_title="Konaklama Raporu", layout="wide")

def login():
    st.sidebar.header("🔐 Giriş Yap")
    username = st.sidebar.text_input("Kullanıcı Adı")
    password = st.sidebar.text_input("Şifre", type="password")
    if st.sidebar.button("Giriş"):
        if username == "admin" and password == "sifre123":
            st.session_state["authenticated"] = True
        else:
            st.sidebar.error("Hatalı kullanıcı adı veya şifre")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

st.success("Giriş başarılı. Soldan rapor sayfası seçebilirsiniz.")
