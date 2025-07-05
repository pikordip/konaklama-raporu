import pandas as pd
import streamlit as st

st.set_page_config(page_title="Konaklama Raporu", layout="wide")

# Giriş
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

st.title("🏨 Konaklama Analiz Raporu")

# Excel yükle
uploaded_file = st.sidebar.file_uploader("📂 Excel Dosyasını Yükle (.xlsx)", type=["xlsx"])

# Cache'lenmiş veri hazırlama fonksiyonu
@st.cache_data
def oku_ve_temizle(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df[df['Kod 3'] != 'XXX']
    if 'İntern Notu' in df.columns:
        df = df[~df['İntern Notu'].astype(str).str.upper().str.contains("BLOKAJ")]
    df = df[df['Yetişkin'] == 2]

    df['Giriş Tarihi'] = pd.to_datetime(df['Giriş Tarihi'])
    df['Çıkış Tarihi'] = pd.to_datetime(df['Çıkış Tarihi'])
    df['Otel Alış Tar.'] = pd.to_datetime(df['Otel Alış Tar.'])
    df['Geceleme'] = (df['Çıkış Tarihi'] - df['Giriş Tarihi']).dt.days
    df['Geceleme'] = df['Geceleme'].apply(lambda x: x if x > 0 else 1)
    df['Kişi_Geceleme'] = df['Geceleme'] * 2

    aylar = {1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
             7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"}

    df['Giriş Ayı'] = df['Giriş Tarihi'].dt.month.map(aylar)
    df['Otel Alış Ayı'] = df['Otel Alış Tar.'].dt.month.map(aylar) + " " + df['Otel Alış Tar.'].dt.year.astype(str)
    df['Otel Alış Ayı Sıra'] = df['Otel Alış Tar.'].dt.strftime('%Y-%m')
    return df.sort_values("Otel Alış Ayı Sıra")

# Rapor cache (filtreli hal için bile)
@st.cache_data
def rapor_hazirla(df):
    return (
        df.groupby(['Operatör Adı', 'Bölge', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı', 'Giriş Ayı'])
        .agg(
            Toplam_Tutar=('Total Alış Fat.', 'sum'),
            Toplam_Kisi_Geceleme=('Kişi_Geceleme', 'sum')
        )
        .reset_index()
        .assign(Kişi_Başı_Geceleme=lambda x: x['Toplam_Tutar'] / x['Toplam_Kisi_Geceleme'])
    )

if uploaded_file is not None:
    df = oku_ve_temizle(uploaded_file)

    st.sidebar.header("🔎 Filtreler")
    oteller = st.sidebar.multiselect("🏨 Otel", sorted(df["Otel Adı"].dropna().unique()))
    operatörler = st.sidebar.multiselect("🧳 Operatör", sorted(df["Operatör Adı"].dropna().unique()))
    odalar = st.sidebar.multiselect("🛏️ Oda Tipi", sorted(df["Oda Tipi Tanmı"].dropna().unique()))

    df_filtreli = df.copy()
    if oteller:
        df_filtreli = df_filtreli[df_filtreli['Otel Adı'].isin(oteller)]
    if operatörler:
        df_filtreli = df_filtreli[df_filtreli['Operatör Adı'].isin(operatörler)]
    if odalar:
        df_filtreli = df_filtreli[df_filtreli['Oda Tipi Tanmı'].isin(odalar)]

    rapor = rapor_hazirla(df_filtreli)

    pivot = rapor.pivot_table(
        index=['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı'],
        columns='Giriş Ayı',
        values='Kişi_Başı_Geceleme',
        aggfunc='mean'
    ).applymap(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")

    st.markdown("### 📊 Kişi Başı Geceleme Fiyatları")
    st.dataframe(pivot, use_container_width=True)

else:
    st.warning("Lütfen sol menüden Excel dosyasını yükleyin.")
