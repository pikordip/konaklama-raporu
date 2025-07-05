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
    # … (önceki load_data fonksiyonundaki veri temizleme ve dönüşümler) …
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

# … geri kalan raporlama ve filtreleme kodun aynen kalsın …
