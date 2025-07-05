import streamlit as st
import os
import glob
import time
import pandas as pd

# 🔐 Şifreli giriş kontrolü
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Lütfen ana sayfadan giriş yapın.")
    st.stop()

# 🌐 Sayfa yapılandırması
st.set_page_config(page_title="Rezervasyon Tarihine Göre Rapor", layout="wide")
st.title("📊 Rezervasyon Tarihine Göre Kişi Başı Geceleme Tutarı")

# 📁 Tek Excel dosyasını data klasöründen bul
data_files = glob.glob("data/*.xlsx")
if not data_files:
    st.error("❌ 'data' klasöründe .xlsx uzantılı dosya bulunamadı!")
    st.stop()

file_path = data_files[0]

# ⏰ Dosya değişiklik tarihini al
timestamp = os.path.getmtime(file_path)
last_modified_date = time.strftime("%d.%m.%Y", time.localtime(timestamp))
st.markdown(f"**📅 Veri Güncelleme Tarihi:** `{last_modified_date}`")

# 📄 Excel verisini yükle
@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()

    df = df[df['Kod 3'] != 'XXX']
    if 'İntern Notu' in df.columns:
        df = df[~df['İntern Notu'].astype(str).str.upper().str.contains("BLOKAJ")]
    df = df[df['Yetişkin'] == 2]

    for col in ['Extra Bed', 'Çocuk', 'Bebek']:
        if col in df.columns:
            df = df[(df[col].isna()) | (df[col] == 0)]

    df['Giriş Tarihi'] = pd.to_datetime(df['Giriş Tarihi'], errors='coerce')
    df['Çıkış Tarihi'] = pd.to_datetime(df['Çıkış Tarihi'], errors='coerce')
    df['Otel Alış Tar.'] = pd.to_datetime(df['Otel Alış Tar.'], errors='coerce')

    df['Geceleme'] = (df['Çıkış Tarihi'] - df['Giriş Tarihi']).dt.days
    df['Geceleme'] = df['Geceleme'].apply(lambda x: x if x > 0 else 1)
    df['Kişi_Geceleme'] = df['Geceleme'] * 2

    aylar = {
        1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
        7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"
    }

    df['Giriş Ayı'] = df['Giriş Tarihi'].dt.month
    df['Giriş Ayı İsim'] = df['Giriş Ayı'].map(aylar)

    df['Otel Alış Ayı'] = df['Otel Alış Tar.'].dt.to_period("M").astype(str)
    df['Otel Alış Ayı Sıra'] = df['Otel Alış Tar.'].dt.strftime('%Y-%m')
    df['Otel Alış Ayı Etiket'] = df['Otel Alış Tar.'].dt.month.map(aylar) + " " + df['Otel Alış Tar.'].dt.year.astype(str)

    return df

df = load_data(file_path)

# 🔔 Bilgilendirme Notu
st.info("🔒 *Bu rapor yalnızca 2 yetişkin içeren ve çocuk, bebek veya ekstra yatak içermeyen rezervasyonları kapsamaktadır.*")

# 🔎 Dinamik filtreler
st.sidebar.header("🔎 Filtreler")

otel_options = sorted(df["Otel Adı"].dropna().unique())
selected_oteller = st.sidebar.multiselect("🏨 Otel", options=otel_options)

filtered_df = df[df["Otel Adı"].isin(selected_oteller)] if selected_oteller else df
operatör_options = sorted(filtered_df["Operatör Adı"].dropna().unique())
selected_operatörler = st.sidebar.multiselect("🧳 Operatör", options=operatör_options)

filtered_df = filtered_df[filtered_df["Operatör Adı"].isin(selected_operatörler)] if selected_operatörler else filtered_df
oda_options = sorted(filtered_df["Oda Tipi Tanmı"].dropna().unique())
selected_odalar = st.sidebar.multiselect("🛏️ Oda Tipi", options=oda_options)

# Filtreleri uygula
df_f = df.copy()
if selected_oteller:
    df_f = df_f[df_f["Otel Adı"].isin(selected_oteller)]
if selected_operatörler:
    df_f = df_f[df_f["Operatör Adı"].isin(selected_operatörler)]
if selected_odalar:
    df_f = df_f[df_f["Oda Tipi Tanmı"].isin(selected_odalar)]

# 📊 Raporu oluştur
rapor = (
    df_f.groupby([
        'Operatör Adı', 'Bölge', 'Otel Adı', 'Oda Tipi Tanmı',
        'Otel Alış Ayı Sıra', 'Otel Alış Ayı Etiket',
        'Giriş Ayı İsim', 'Giriş Ayı'
    ])
    .agg(
        Toplam_Tutar=('Total Alış Fat.', 'sum'),
        Toplam_Kisi_Geceleme=('Kişi_Geceleme', 'sum')
    )
    .reset_index()
)
rapor['Kişi Başı Geceleme (€)'] = rapor['Toplam_Tutar'] / rapor['Toplam_Kisi_Geceleme']

# 📌 Pivot tablo oluştur
pivot = rapor.pivot_table(
    index=['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı Sıra', 'Otel Alış Ayı Etiket'],
    columns='Giriş Ayı İsim',
    values='Kişi Başı Geceleme (€)',
    aggfunc='mean'
)

# 🧹 Ay sıralaması
ay_sirali = ["OCAK", "ŞUBAT", "MART", "NİSAN", "MAYIS", "HAZİRAN",
             "TEMMUZ", "AĞUSTOS", "EYLÜL", "EKİM", "KASIM", "ARALIK"]
pivot = pivot[[col for col in ay_sirali if col in pivot.columns]]

# 📋 Alış ayına göre sıralama
pivot = pivot.reset_index().sort_values(by="Otel Alış Ayı Sıra")
pivot = pivot.drop(columns='Otel Alış Ayı Sıra')
pivot.set_index(['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı Etiket'], inplace=True)

# 💶 Sayısal verileri formatla
pivot = pivot.applymap(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")

# 📈 Görselleştirme
st.markdown("### 📈 Kişi Başı Geceleme Tutarları (Giriş Aylarına Göre)")
st.dataframe(pivot, use_container_width=True)
