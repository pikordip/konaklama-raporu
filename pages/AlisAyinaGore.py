if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Lütfen ana sayfadan giriş yapın.")
    st.stop()


import os
import glob
import time
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Konaklama Raporu", layout="wide")

# data klasöründeki ilk .xlsx dosyasını bul (sadece 1 dosya olmalı)
data_files = glob.glob("data/*.xlsx")
if len(data_files) == 0:
    st.error("Data klasöründe hiç Excel dosyası bulunamadı!")
    st.stop()

file_path = data_files[0]

# Dosya değişiklik tarihini al
timestamp = os.path.getmtime(file_path)
last_modified_date = time.strftime("%d.%m.%Y", time.localtime(timestamp))
st.markdown(f"**Veri Güncelleme Tarihi (Dosya Sistemi):** {last_modified_date}")

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
    df['Otel Alış Ayı'] = df['Otel Alış Tar.'].dt.month.map(aylar) + " " + df['Otel Alış Tar.'].dt.year.astype(str)
    df['Otel Alış Ayı Sıra'] = df['Otel Alış Tar.'].dt.strftime('%Y-%m')

    return df.sort_values("Otel Alış Ayı Sıra")

df = load_data(file_path)

# Dinamik filtre seçeneklerini hesapla
# Başlangıçta tüm unique değerler
otel_options = sorted(df["Otel Adı"].dropna().unique())
operatör_options = sorted(df["Operatör Adı"].dropna().unique())
oda_options = sorted(df["Oda Tipi Tanmı"].dropna().unique())

# Otel seçimi
selected_oteller = st.sidebar.multiselect("🏨 Otel", options=otel_options)

# Otel seçilmişse, o otellere göre operatörleri filtrele
if selected_oteller:
    operatör_options = sorted(df[df["Otel Adı"].isin(selected_oteller)]["Operatör Adı"].dropna().unique())

selected_operatörler = st.sidebar.multiselect("🧳 Operatör", options=operatör_options)

# Otel ve operatör seçilmişse, oda tiplerini filtrele
df_for_oda = df.copy()
if selected_oteller:
    df_for_oda = df_for_oda[df_for_oda["Otel Adı"].isin(selected_oteller)]
if selected_operatörler:
    df_for_oda = df_for_oda[df_for_oda["Operatör Adı"].isin(selected_operatörler)]

oda_options = sorted(df_for_oda["Oda Tipi Tanmı"].dropna().unique())
selected_odalar = st.sidebar.multiselect("🛏️ Oda Tipi", options=oda_options)

# Filtreli dataframe oluştur
df_filtreli = df.copy()
if selected_oteller:
    df_filtreli = df_filtreli[df_filtreli['Otel Adı'].isin(selected_oteller)]
if selected_operatörler:
    df_filtreli = df_filtreli[df_filtreli['Operatör Adı'].isin(selected_operatörler)]
if selected_odalar:
    df_filtreli = df_filtreli[df_filtreli['Oda Tipi Tanmı'].isin(selected_odalar)]

# Rapor oluşturma
rapor = (
    df_filtreli.groupby(['Operatör Adı', 'Bölge', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı', 'Giriş Ayı'])
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

st.markdown("### 📊 Kişi Başı Geceleme Fiyatları (Aylara Göre)")
st.dataframe(pivot, use_container_width=True)
