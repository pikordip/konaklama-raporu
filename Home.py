import pandas as pd
import streamlit as st

st.set_page_config(page_title="Konaklama Raporu", layout="wide")
st.title("🏨 Konaklama Analiz Raporu")

@st.cache_data
def load_data(file_name="AKAY2025.xlsx"):
    file_path = f"data/{file_name}"  # GitHub'daki data klasörü yolu
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    df['Otel Alış Tar.'] = pd.to_datetime(df['Otel Alış Tar.'], errors='coerce')
    df['Giriş Tarihi'] = pd.to_datetime(df['Giriş Tarihi'], errors='coerce')
    df['Çıkış Tarihi'] = pd.to_datetime(df['Çıkış Tarihi'], errors='coerce')

    # Temizleme
    df = df[df['Kod 3'] != 'XXX']
    df = df[df['Yetişkin'] == 2]
    df = df[~df.get('İntern Notu', '').astype(str).str.upper().str.contains("BLOKAJ")]

    df['Geceleme'] = (df['Çıkış Tarihi'] - df['Giriş Tarihi']).dt.days
    df['Geceleme'] = df['Geceleme'].apply(lambda x: x if x > 0 else 1)
    df['Kişi_Geceleme'] = df['Geceleme'] * 2

    return df

def get_last_update(df):
    max_date = df['Otel Alış Tar.'].max()
    if pd.isna(max_date):
        return "Bilinmiyor"
    return max_date.strftime("%d.%m.%Y")

# 🔍 Kullanıcının dosya seçmesi için seçenek
file_options = ["AKAY2024.xlsx", "AKAY2025.xlsx"]
selected_file = st.sidebar.selectbox("📁 Veri Dosyası Seçin", file_options)

# 📄 Veri yükle ve güncelleme tarihi göster
df = load_data(selected_file)
last_update = get_last_update(df)
st.markdown(f"**📅 Veri Güncelleme Tarihi:** `{last_update}`")
st.markdown(f"**📂 Seçilen Dosya:** `{selected_file}`")

# 🔎 Otel, Operatör, Oda Tipi filtreleri (isteğe bağlı)
st.sidebar.header("🔎 Filtreler")
oteller = st.sidebar.multiselect("🏨 Otel", sorted(df["Otel Adı"].dropna().unique()))
operatörler = st.sidebar.multiselect("🧳 Operatör", sorted(df["Operatör Adı"].dropna().unique()))
odalar = st.sidebar.multiselect("🛏️ Oda Tipi", sorted(df["Oda Tipi Tanmı"].dropna().unique()))

df_f = df.copy()
if oteller:
    df_f = df_f[df_f["Otel Adı"].isin(oteller)]
if operatörler:
    df_f = df_f[df_f["Operatör Adı"].isin(operatörler)]
if odalar:
    df_f = df_f[df_f["Oda Tipi Tanmı"].isin(odalar)]

# 🧾 Veri tablosunu göster
st.markdown("### 📊 Filtrelenmiş Veri")
st.dataframe(df_f, use_container_width=True)
