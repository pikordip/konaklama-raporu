import streamlit as st
import os
import time
import pandas as pd

# 💻 Şifre kontrolü
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Lütfen ana sayfadan giriş yapın.")
    st.stop()

# 🌐 Sayfa ayarları
st.set_page_config(page_title="Giriş Tarihine Göre Rapor", layout="wide")
st.title("📊 Giriş Ayına Göre Kişi Başı Geceleme Tutarları")

# 📁 Tek Excel dosyasını otomatik bul
def find_excel_file():
    files = os.listdir("data")
    for f in files:
        if f.endswith(".xlsx"):
            return f
    return None

file_name = find_excel_file()
if not file_name:
    st.error("❌ 'data' klasöründe .xlsx dosyası bulunamadı!")
    st.stop()

file_path = f"data/{file_name}"

# ⏳ Dosya değişiklik tarihi
timestamp = os.path.getmtime(file_path)
last_modified_date = time.strftime("%d.%m.%Y", time.localtime(timestamp))
st.markdown(f"**📅 Veri Güncelleme Tarihi:** `{last_modified_date}`")

# 📄 Veriyi yükle
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

    df['Geceleme'] = (df['Çıkış Tarihi'] - df['Giriş Tarihi']).dt.days
    df['Geceleme'] = df['Geceleme'].apply(lambda x: x if x > 0 else 1)
    df['Kişi_Geceleme'] = df['Geceleme'] * 2

    aylar = {
        1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
        7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"
    }

    df['Giriş Ayı No'] = df['Giriş Tarihi'].dt.month
    df['Giriş Ayı'] = df['Giriş Ayı No'].map(aylar)

    return df

df = load_data(file_path)

# 🔔 Bilgilendirme Notu
st.info("🔒 *Bu rapor yalnızca 2 yetişkin içeren ve çocuk, bebek veya ekstra yatak içermeyen rezervasyonları kapsamaktadır.*")

# 🔍 Dinamik filtreleme (bağlantılı)
st.sidebar.header("🔎 Filtreler")

otel_options = sorted(df["Otel Adı"].dropna().unique())
selected_oteller = st.sidebar.multiselect("🏨 Otel", options=otel_options)

filtered_df_for_op = df[df["Otel Adı"].isin(selected_oteller)] if selected_oteller else df
operatör_options = sorted(filtered_df_for_op["Operatör Adı"].dropna().unique())
selected_operatörler = st.sidebar.multiselect("🧳 Operatör", options=operatör_options)

filtered_df_for_oda = filtered_df_for_op[filtered_df_for_op["Operatör Adı"].isin(selected_operatörler)] if selected_operatörler else filtered_df_for_op
oda_options = sorted(filtered_df_for_oda["Oda Tipi Tanmı"].dropna().unique())
selected_odalar = st.sidebar.multiselect("🛏️ Oda Tipi", options=oda_options)

# 📌 Filtreleri uygula
df_f = df.copy()
if selected_oteller:
    df_f = df_f[df_f["Otel Adı"].isin(selected_oteller)]
if selected_operatörler:
    df_f = df_f[df_f["Operatör Adı"].isin(selected_operatörler)]
if selected_odalar:
    df_f = df_f[df_f["Oda Tipi Tanmı"].isin(selected_odalar)]

# 📊 Pivot rapor fonksiyonu
@st.cache_data
def rapor_giris_ayi(df):
    return (
        df.groupby(['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı', 'Giriş Ayı', 'Giriş Ayı No'])
        .agg(
            Toplam_Tutar=('Total Alış Fat.', 'sum'),
            Toplam_Kisi_Geceleme=('Kişi_Geceleme', 'sum')
        )
        .reset_index()
        .assign(Kişi_Başı_Geceleme=lambda x: x['Toplam_Tutar'] / x['Toplam_Kisi_Geceleme'])
    )

rapor = rapor_giris_ayi(df_f)

# 📌 Pivot tablo
pivot = rapor.pivot_table(
    index=['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı'],
    columns='Giriş Ayı',
    values='Kişi_Başı_Geceleme',
    aggfunc='mean'
)

# 📅 Ayları doğru sırala
ay_sirali = ["OCAK", "ŞUBAT", "MART", "NİSAN", "MAYIS", "HAZİRAN",
             "TEMMUZ", "AĞUSTOS", "EYLÜL", "EKİM", "KASIM", "ARALIK"]
pivot = pivot[[ay for ay in ay_sirali if ay in pivot.columns]]

# 💶 Formatla
pivot = pivot.applymap(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")

# 📈 Sonuç
st.markdown("### 📈 Giriş Ayına Göre Kişi Başı Geceleme Tutarları")
st.dataframe(pivot, use_container_width=True)
