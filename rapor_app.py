import pandas as pd
import streamlit as st

st.set_page_config(page_title="Konaklama Raporu", layout="wide")

# --- Basit kullanıcı doğrulama ---
def login():
    st.sidebar.header("Giriş Yapınız")
    username = st.sidebar.text_input("Kullanıcı Adı")
    password = st.sidebar.text_input("Şifre", type="password")
    if st.sidebar.button("Giriş"):
        if username == "admin" and password == "sifre123":
            st.session_state["authenticated"] = True
        else:
            st.sidebar.error("Hatalı kullanıcı adı veya şifre")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

st.title("🏨 Konaklama Analiz Raporu")

def temizle_ve_hazirla(df):
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

    aylar_tr = {
        1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
        7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"
    }
    df['Giriş Ayı'] = df['Giriş Tarihi'].dt.month.map(aylar_tr)
    df['Otel Alış Ayı'] = df['Otel Alış Tar.'].dt.month.map(aylar_tr) + " " + df['Otel Alış Tar.'].dt.year.astype(str)
    df['Otel Alış Ayı Sıra'] = df['Otel Alış Tar.'].dt.strftime('%Y-%m')
    df = df.sort_values("Otel Alış Ayı Sıra")
    return df

uploaded_file = st.sidebar.file_uploader("Excel Dosyasını Yükleyin (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df = temizle_ve_hazirla(df)

    # Filtreler
    st.sidebar.header("🔎 Filtrele")
    secili_otel = st.sidebar.multiselect("Otel Seçin", sorted(df["Otel Adı"].dropna().unique()))
    secili_operatör = st.sidebar.multiselect("Operatör Seçin", sorted(df["Operatör Adı"].dropna().unique()))
    secili_oda = st.sidebar.multiselect("Oda Tipi Seçin", sorted(df["Oda Tipi Tanmı"].dropna().unique()))

    if secili_otel:
        df = df[df["Otel Adı"].isin(secili_otel)]
    if secili_operatör:
        df = df[df["Operatör Adı"].isin(secili_operatör)]
    if secili_oda:
        df = df[df["Oda Tipi Tanmı"].isin(secili_oda)]

    # Rapor hesaplama
    rapor = (
        df.groupby(['Operatör Adı', 'Bölge', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı', 'Giriş Ayı'])
        .agg(
            Toplam_Tutar=('Total Alış Fat.', 'sum'),
            Toplam_Kisi_Geceleme=('Kişi_Geceleme', 'sum')
        )
        .reset_index()
    )
    rapor['Kişi Başı Geceleme (€)'] = rapor['Toplam_Tutar'] / rapor['Toplam_Kisi_Geceleme']

    # Pivot tablo oluşturma
    pivot = rapor.pivot_table(
        index=['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı'],
        columns='Giriş Ayı',
        values='Kişi Başı Geceleme (€)',
        aggfunc='mean'
    ).applymap(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")

    st.markdown("### 📊 Kişi Başı Geceleme Fiyatları")
    st.dataframe(pivot, use_container_width=True)

else:
    st.warning("Lütfen Excel dosyanızı yukarıdaki alandan yükleyin.")
