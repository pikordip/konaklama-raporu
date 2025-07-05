import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Giriş Tarihine Göre Rapor", layout="wide")

# Tek Excel dosyasını data klasöründen otomatik bul
def find_excel_file():
    files = os.listdir("data")
    for f in files:
        if f.endswith(".xlsx"):
            return f
    return None

file_name = find_excel_file()
if file_name is None:
    st.error("Data klasöründe .xlsx uzantılı dosya bulunamadı!")
    st.stop()

file_path = f"data/{file_name}"

@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
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

    return df

df = load_data(file_path)

# Veri güncelleme tarihi
last_update = df['Otel Alış Tar.'].max().strftime("%d.%m.%Y")
st.markdown(f"**Veri Güncelleme Tarihi:** {last_update}")

# Filtreler
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

@st.cache_data
def rapor_giris_ayi(df):
    return (
        df.groupby(['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı', 'Giriş Ayı'])
        .agg(
            Toplam_Tutar=('Total Alış Fat.', 'sum'),
            Toplam_Kisi_Geceleme=('Kişi_Geceleme', 'sum')
        )
        .reset_index()
        .assign(Kişi_Başı_Geceleme=lambda x: x['Toplam_Tutar'] / x['Toplam_Kisi_Geceleme'])
    )

rapor = rapor_giris_ayi(df_filtreli)

pivot = rapor.pivot_table(
    index=['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı'],
    columns='Giriş Ayı',
    values='Kişi_Başı_Geceleme',
    aggfunc='mean'
).applymap(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")

st.markdown("### 📊 Giriş Ayına Göre Kişi Başı Geceleme Fiyatları")
st.dataframe(pivot, use_container_width=True)
