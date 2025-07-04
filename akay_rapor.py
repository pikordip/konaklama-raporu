import pandas as pd
import streamlit as st

st.set_page_config(page_title="Konaklama Raporu", layout="wide")
st.title("🏨 Konaklama Analiz Raporu")

@st.cache_data
def load_data():
    file_path = r"C:\Users\metin\OneDrive\Masaüstü\akay\AKAY2024.xlsx"
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    # Temizlik ve filtreleme
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

    # Aylar
    ay_adlari = {
        1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
        7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"
    }
    df['Giriş Ayı'] = df['Giriş Tarihi'].dt.month.map(ay_adlari)

    df['Otel Alış Ayı'] = df['Otel Alış Tar.'].dt.strftime("%b%y").str.upper()
    df['Otel Alış Ayı Sıra'] = df['Otel Alış Tar.'].dt.strftime('%Y-%m')
    df = df.sort_values("Otel Alış Ayı Sıra")

    return df

df = load_data()

# 📌 Filtreler
st.sidebar.header("🔎 Filtrele")

operator_sec = st.sidebar.multiselect("Operatör Seçin", df["Operatör Adı"].unique())
otel_sec = st.sidebar.multiselect("Otel Seçin", df["Otel Adı"].unique())
oda_tipi_sec = st.sidebar.multiselect("Oda Tipi Seçin", df["Oda Tipi Tanmı"].dropna().unique())

giris_tarih_sec = st.sidebar.date_input(
    "Giriş Tarihi Aralığı Seçin",
    value=(df['Giriş Tarihi'].min(), df['Giriş Tarihi'].max())
)

if operator_sec:
    df = df[df['Operatör Adı'].isin(operator_sec)]
if otel_sec:
    df = df[df['Otel Adı'].isin(otel_sec)]
if oda_tipi_sec:
    df = df[df['Oda Tipi Tanmı'].isin(oda_tipi_sec)]
if isinstance(giris_tarih_sec, tuple) and len(giris_tarih_sec) == 2:
    start_date, end_date = giris_tarih_sec
    df = df[(df['Giriş Tarihi'] >= pd.to_datetime(start_date)) & (df['Giriş Tarihi'] <= pd.to_datetime(end_date))]

# 📊 RAPOR
rapor = (
    df
    .groupby(['Operatör Adı', 'Bölge', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı', 'Giriş Ayı'])
    .agg(
        Toplam_Tutar=('Total Alış Fat.', 'sum'),
        Toplam_Kisi_Geceleme=('Kişi_Geceleme', 'sum')
    )
    .reset_index()
)

rapor['Kişi Başı Geceleme (€)'] = rapor['Toplam_Tutar'] / rapor['Toplam_Kisi_Geceleme']

pivot = rapor.pivot_table(
    index=['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı'],
    columns='Giriş Ayı',
    values='Kişi Başı Geceleme (€)',
    aggfunc='mean'
).applymap(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")

st.markdown("### 📊 Kişi Başı Geceleme Fiyatları")
st.dataframe(pivot, use_container_width=True)
