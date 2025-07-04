import pandas as pd
import streamlit as st

# 🔐 GİRİŞ EKRANI
def login():
    st.sidebar.title("🔐 Giriş Yap")
    username = st.sidebar.text_input("Kullanıcı Adı")
    password = st.sidebar.text_input("Şifre", type="password")
    if username == "admin" and password == "1234":
        return True
    elif username and password:
        st.sidebar.warning("🚫 Hatalı kullanıcı adı veya şifre")
    return False

# 🔐 Giriş doğruysa uygulamayı başlat
if login():

    st.set_page_config(page_title="Konaklama Raporu", layout="wide")
    st.title("🏨 Konaklama Analiz Merkezi")

    # 📑 Sayfa Seçici Menü
    sayfa = st.selectbox("📄 Rapor Türünü Seçin", [
        "📘 Otel Alış ve Giriş Ayına Göre Rapor",
        "📙 Sadece Giriş Ayına Göre Rapor"
    ])

    @st.cache_data
    def load_data():
        file_path = r"C:\Users\metin\OneDrive\Masaüstü\akay\AKAY2024.xlsx"
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()

        # Temizlik ve filtreler
        df = df[df['Kod 3'] != 'XXX']
        if 'İntern Notu' in df.columns:
            df = df[~df['İntern Notu'].astype(str).str.upper().str.contains("BLOKAJ")]
        df = df[df['Yetişkin'] == 2]

        # Tarihler
        df['Giriş Tarihi'] = pd.to_datetime(df['Giriş Tarihi'])
        df['Çıkış Tarihi'] = pd.to_datetime(df['Çıkış Tarihi'])
        df['Otel Alış Tar.'] = pd.to_datetime(df['Otel Alış Tar.'])

        # Geceleme hesaplamaları
        df['Geceleme'] = (df['Çıkış Tarihi'] - df['Giriş Tarihi']).dt.days
        df['Geceleme'] = df['Geceleme'].apply(lambda x: x if x > 0 else 1)
        df['Kişi_Geceleme'] = df['Geceleme'] * 2

        # Aylar (Türkçe)
        aylar_tr = {
            1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
            7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"
        }
        df['Giriş Ayı'] = df['Giriş Tarihi'].dt.month.map(aylar_tr)
        df['Giriş Ayı Sıra'] = df['Giriş Tarihi'].dt.strftime('%Y-%m')

        df['Otel Alış Ayı'] = df['Otel Alış Tar.'].dt.month.map(aylar_tr) + " " + df['Otel Alış Tar.'].dt.year.astype(str)
        df['Otel Alış Ayı Sıra'] = df['Otel Alış Tar.'].dt.strftime('%Y-%m')

        return df

    df = load_data()

    # 🔎 Ortak Filtreler
    st.sidebar.header("🔎 Filtrele")
    secili_otel = st.sidebar.multiselect("Otel Seçin", sorted(df["Otel Adı"].dropna().unique()))
    secili_operatör = st.sidebar.multiselect("Operatör Seçin", sorted(df["Operatör Adı"].dropna().unique()))
    secili_oda = st.sidebar.multiselect("Oda Tipi Seçin", sorted(df["Oda Tipi Tanmı"].dropna().unique()))

    df_filtered = df.copy()
    if secili_otel:
        df_filtered = df_filtered[df_filtered["Otel Adı"].isin(secili_otel)]
    if secili_operatör:
        df_filtered = df_filtered[df_filtered["Operatör Adı"].isin(secili_operatör)]
    if secili_oda:
        df_filtered = df_filtered[df_filtered["Oda Tipi Tanmı"].isin(secili_oda)]

    # 📘 SAYFA 1: Giriş ve Alış Ayı
    if sayfa == "📘 Otel Alış ve Giriş Ayına Göre Rapor":
        st.markdown("### 📘 Kişi Başı Geceleme Fiyatları (Giriş Ayı ve Otel Alış Ayına Göre)")

        rapor1 = (
            df_filtered
            .groupby(['Operatör Adı', 'Bölge', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı', 'Otel Alış Ayı Sıra', 'Giriş Ayı'])
            .agg(
                Toplam_Tutar=('Total Alış Fat.', 'sum'),
                Toplam_Kisi_Geceleme=('Kişi_Geceleme', 'sum')
            )
            .reset_index()
        )
        rapor1['Kişi Başı Geceleme (€)'] = rapor1['Toplam_Tutar'] / rapor1['Toplam_Kisi_Geceleme']
        rapor1 = rapor1.sort_values("Otel Alış Ayı Sıra")

        pivot1 = rapor1.pivot_table(
            index=['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı'],
            columns='Giriş Ayı',
            values='Kişi Başı Geceleme (€)',
            aggfunc='mean'
        ).applymap(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")

        st.dataframe(pivot1, use_container_width=True)

    # 📙 SAYFA 2: Giriş Ayı
    elif sayfa == "📙 Sadece Giriş Ayına Göre Rapor":
        st.markdown("### 📙 Kişi Başı Geceleme Fiyatları (Yalnızca Giriş Ayına Göre)")

        rapor2 = (
            df_filtered
            .groupby(['Operatör Adı', 'Bölge', 'Otel Adı', 'Oda Tipi Tanmı', 'Giriş Ayı'])
            .agg(
                Toplam_Tutar=('Total Alış Fat.', 'sum'),
                Toplam_Kisi_Geceleme=('Kişi_Geceleme', 'sum')
            )
            .reset_index()
        )
        rapor2['Kişi Başı Geceleme (€)'] = rapor2['Toplam_Tutar'] / rapor2['Toplam_Kisi_Geceleme']

        pivot2 = rapor2.pivot_table(
            index=['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı'],
            columns='Giriş Ayı',
            values='Kişi Başı Geceleme (€)',
            aggfunc='mean'
        ).applymap(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")

        st.dataframe(pivot2, use_container_width=True)
