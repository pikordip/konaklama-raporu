# 📌 Pivot tablo oluşturma
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

# 📋 Alış ayına göre tarihsel sıralama
pivot = pivot.reset_index().sort_values(by='Otel Alış Ayı Sıra')

# ❌ Artık sıralama için kullanılan 'Otel Alış Ayı Sıra' sütununu göstermek istemiyoruz
pivot = pivot.drop(columns='Otel Alış Ayı Sıra')

# 🔁 Yeniden uygun şekilde index ayarla
pivot.set_index(['Operatör Adı', 'Otel Adı', 'Oda Tipi Tanmı', 'Otel Alış Ayı Etiket'], inplace=True)

# 💶 Sayısal verileri € formatına çevir
pivot = pivot.applymap(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")
