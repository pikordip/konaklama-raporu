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

    # Temizleme
    df = df[df['Kod 3'] != 'XXX']
    df = df[df['Yetişkin'] == 2]

    return df

def get_last_update(df):
    max_date = df['Otel Alış Tar.'].max()
    if pd.isna(max_date):
        return "Bilinmiyor"
    return max_date.strftime("%d.%m.%Y")

# DİLEĞE BAĞLI: Dosya adını sidebar'dan seçilebilir yapmak istersen:
file_options = ["AKAY2024.xlsx", "AKAY2025.xlsx"]
selected_file = st.sidebar.selectbox("Veri Dosyası Seçin", file_options)

df = load_data(selected_file)
last_update = get_last_update(df)
st.markdown(f"**Veri Güncelleme Tarihi:** {last_update}")

# Burada devam eden analiz kodunu yazabilirsin
# Örnek:
st.write(f"Seçilen dosya: {selected_file}")
st.dataframe(df.head())
