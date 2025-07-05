import pandas as pd
import streamlit as st

st.set_page_config(page_title="Giriş Ayına Göre Rapor", layout="wide")
st.title("📅 Giriş Ayına Göre Konaklama Raporu")

# 🔁 Excel dosyasını yükle
@st.cache_data
def load_data(file_name="AKAY2025.xlsx"):
    file_path = f"data/{file_name}"
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    df = df[df['Kod 3'] != 'XXX']
    if 'İntern Notu' in df.columns:
        df = df[~df['İntern Notu'].astype(str).str.upper().str.contains("BLOKAJ")]
    df = df[df['Yetişkin'] == 2]

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

    df['Giriş Ayı'] = df['Giriş Tarihi'].dt.month.map(aylar)
    return df

# ⏱️ Güncelleme tarihi
def get_last_update(df):
    max_date = df['Otel Alış Tar.'].max()
    return max_date.strftime("%d.%m.%Y") if pd.notnull(max_date) else "Bilinmiyor"

# 🔄 Yükle
df = load_data("AKAY2025.xlsx")
last_update = get_last_update(df)

st.markdown(f"**📅 Veri Güncelleme Tarihi:** `{last_update}`")

# 🎛️ Filtresi
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

# 📊 Rapor
rapor = (
    df_f.groupby(['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı', 'Giriş Ayı'])
    .agg(
        Toplam_Tutar=('Total Alış Fat.', 'sum'),
        Toplam_Kisi_Geceleme=('Kişi_Geceleme', 'sum')
    )
    .reset_index()
)
rapor['Kişi Başı Geceleme (€)'] = rapor['Toplam_Tutar'] / rapor['Toplam_Kisi_Geceleme']

pivot = rapor.pivot_table(
    index=['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı'],
    columns='Giriş Ayı',
    values='Kişi Başı Geceleme (€)',
    aggfunc='mean'
).applymap(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")

st.markdown("### 📊 Giriş Ayına Göre Kişi Başı Geceleme Fiyatları")
st.dataframe(pivot, use_container_width=True)
