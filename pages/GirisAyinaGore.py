import pandas as pd
import streamlit as st

st.set_page_config(page_title="Giriş Tarihine Göre Rapor", layout="wide")

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Lütfen ana sayfadan giriş yapın.")
    st.stop()

if "data" not in st.session_state:
    st.warning("Ana sayfadan veri yüklenmedi.")
    st.stop()

df = st.session_state["data"]

# En güncel alış tarihi
def get_last_update(df):
    max_date = df["Otel Alış Tar."].max()
    if pd.isna(max_date):
        return "Bilinmiyor"
    return max_date.strftime("%d.%m.%Y")

st.title("📅 Giriş Tarihine Göre Konaklama Raporu")
st.markdown(f"**Veri Güncelleme Tarihi:** {get_last_update(df)}")

# Ay ismi eşlemesi
aylar = {
    1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
    7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"
}

if "Giriş Ayı" not in df.columns:
    df["Giriş Ayı"] = df["Giriş Tarihi"].dt.month.map(aylar)

# 🔍 Filtreler
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
@st.cache_data
def rapor_giris_ayi(df):
    return (
        df.groupby(["Operatör Adı", "Otel Adı", "Oda Tipi Tanmı", "Giriş Ayı"])
        .agg(
            Toplam_Tutar=("Total Alış Fat.", "sum"),
            Toplam_Kisi_Geceleme=("Kişi_Geceleme", "sum")
        )
        .reset_index()
        .assign(Kişi_Başı_Geceleme=lambda x: x["Toplam_Tutar"] / x["Toplam_Kisi_Geceleme"])
    )

rapor = rapor_giris_ayi(df_f)

pivot = rapor.pivot_table(
    index=["Operatör Adı", "Otel Adı", "Oda Tipi Tanmı"],
    columns="Giriş Ayı",
    values="Kişi_Başı_Geceleme",
    aggfunc="mean"
).applymap(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")

st.markdown("### 📊 Giriş Ayına Göre Kişi Başı Geceleme Fiyatları")
st.dataframe(pivot, use_container_width=True)
