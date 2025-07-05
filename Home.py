import pandas as pd
import streamlit as st

st.set_page_config(page_title="Konaklama Raporu", layout="wide")
st.title("🏨 Konaklama Analiz Raporu")

@st.cache_data
def load_data(file_name):
    file_path = f"data/{file_name}"
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    # Tarih dönüşümleri, hatalı tarih varsa NaT olur (errors='coerce')
    df['Otel Alış Tar.'] = pd.to_datetime(df['Otel Alış Tar.'], errors='coerce')
    df['Giriş Tarihi'] = pd.to_datetime(df['Giriş Tarihi'], errors='coerce')
    df['Çıkış Tarihi'] = pd.to_datetime(df['Çıkış Tarihi'], errors='coerce')

    # Temizleme işlemleri
    df = df[df['Kod 3'] != 'XXX']
    df = df[df['Yetişkin'] == 2]
    if 'İntern Notu' in df.columns:
        df = df[~df['İntern Notu'].astype(str).str.upper().str.contains("BLOKAJ")]

    # Geceleme hesaplama
    df['Geceleme'] = (df['Çıkış Tarihi'] - df['Giriş Tarihi']).dt.days
    df['Geceleme'] = df['Geceleme'].apply(lambda x: x if x > 0 else 1)
    df['Kişi_Geceleme'] = df['Geceleme'] * 2

    return df

def get_last_update(df):
    max_date = df['Otel Alış Tar.'].max()
    if pd.isna(max_date):
        return "Bilinmiyor"
    return max_date.strftime("%d.%m.%Y")

# Dosya seçimi
file_options = ["AKAY2024.xlsx", "AKAY2025.xlsx"]
selected_file = st.sidebar.selectbox("📁 Veri Dosyası Seçin", file_options)

# Veri yükle
df = load_data(selected_file)

# Veri güncelleme tarihi göster
last_update = get_last_update(df)
st.markdown(f"**📅 Veri Güncelleme Tarihi:** `{last_update}`")
st.markdown(f"**📂 Seçilen Dosya:** `{selected_file}`")

# Dinamik filtre seçeneklerini belirle
otel_options = sorted(df["Otel Adı"].dropna().unique())
operatör_options = sorted(df["Operatör Adı"].dropna().unique())
oda_options = sorted(df["Oda Tipi Tanmı"].dropna().unique())

# Otel filtresi
selected_oteller = st.sidebar.multiselect("🏨 Otel", options=otel_options)

# Otel seçilmişse operatör seçeneklerini filtrele
if selected_oteller:
    operatör_options = sorted(df[df["Otel Adı"].isin(selected_oteller)]["Operatör Adı"].dropna().unique())

selected_operatörler = st.sidebar.multiselect("🧳 Operatör", options=operatör_options)

# Otel ve operatör seçilmişse oda tipi seçeneklerini filtrele
df_for_oda = df.copy()
if selected_oteller:
    df_for_oda = df_for_oda[df_for_oda["Otel Adı"].isin(selected_oteller)]
if selected_operatörler:
    df_for_oda = df_for_oda[df_for_oda["Operatör Adı"].isin(selected_operatörler)]

oda_options = sorted(df_for_oda["Oda Tipi Tanmı"].dropna().unique())
selected_odalar = st.sidebar.multiselect("🛏️ Oda Tipi", options=oda_options)

# Filtrelenmiş dataframe
df_f = df.copy()
if selected_oteller:
    df_f = df_f[df_f["Otel Adı"].isin(selected_oteller)]
if selected_operatörler:
    df_f = df_f[df_f["Operatör Adı"].isin(selected_operatörler)]
if selected_odalar:
    df_f = df_f[df_f["Oda Tipi Tanmı"].isin(selected_odalar)]

# Sonuç gösterimi
st.markdown("### 📊 Filtrelenmiş Veri")
st.dataframe(df_f, use_container_width=True)
