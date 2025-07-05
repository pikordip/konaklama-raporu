if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Lütfen ana sayfadan giriş yapın.")
    st.stop()


import os
import time
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

# Dosya sisteminden dosyanın son değiştirilme tarihini al
timestamp = os.path.getmtime(file_path)
last_modified_date = time.strftime("%d.%m.%Y", time.localtime(timestamp))

st.markdown(f"**Veri Güncelleme Tarihi (Dosya Değişiklik Tarihi):** {last_modified_date}")

# Dinamik filtreleme için seçenekleri güncelle
# Başlangıçta tüm unique değerler
otel_options = sorted(df["Otel Adı"].dropna().unique())
operatör_options = sorted(df["Operatör Adı"].dropna().unique())
oda_options = sorted(df["Oda Tipi Tanmı"].dropna().unique())

# Otel seçimi
selected_oteller = st.sidebar.multiselect("🏨 Otel", options=otel_options)

# Seçilen otellere göre operatör seçeneklerini filtrele
if selected_oteller:
    operatör_options = sorted(df[df["Otel Adı"].isin(selected_oteller)]["Operatör Adı"].dropna().unique())
selected_operatörler = st.sidebar.multiselect("🧳 Operatör", options=operatör_options)

# Seçilen otel ve operatörlere göre oda tipi seçeneklerini filtrele
df_for_oda = df.copy()
if selected_oteller:
    df_for_oda = df_for_oda[df_for_oda["Otel Adı"].isin(selected_oteller)]
if selected_operatörler:
    df_for_oda = df_for_oda[df_for_oda["Operatör Adı"].isin(selected_operatörler)]
oda_options = sorted(df_for_oda["Oda Tipi Tanmı"].dropna().unique())
selected_odalar = st.sidebar.multiselect("🛏️ Oda Tipi", options=oda_options)

# Filtreli veri çerçevesini oluştur
df_filtreli = df.copy()
if selected_oteller:
    df_filtreli = df_filtreli[df_filtreli['Otel Adı'].isin(selected_oteller)]
if selected_operatörler:
    df_filtreli = df_filtreli[df_filtreli['Operatör Adı'].isin(selected_operatörler)]
if selected_odalar:
    df_filtreli = df_filtreli[df_filtreli['Oda Tipi Tanmı'].isin(selected_odalar)]

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
