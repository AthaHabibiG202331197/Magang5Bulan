import pandas as pd
from sqlalchemy import create_engine

# 1. Baca data Excel final
file_path = 'Insight_Khusus_IT_Enterprise.xlsx'
df = pd.read_excel(file_path)

# 2. Konfigurasi Koneksi PostgreSQL (Sesuaikan dengan kredensial Docker/pgAdmin kamu)
# Format: postgresql://username:password@host:port/nama_database
DB_URL = 'postgresql://postgres:a05h07g04@localhost:5432/postgres'

print("Mencoba terhubung ke PostgreSQL...")
try:
    engine = create_engine(DB_URL)
    
    # 3. Masukkan data ke PostgreSQL
    # 'insight_it_enterprise' adalah nama tabel yang akan terbuat otomatis di database
    df.to_sql('insight_it_enterprise', engine, if_exists='replace', index=False)
    
    print(f"Sukses! {len(df)} baris data berhasil dimasukkan ke tabel 'insight_it_enterprise'.")

except Exception as e:
    print(f"Gagal terhubung atau memasukkan data: {e}")
    print("Pastikan container PostgreSQL di Docker sudah 'Running' dan kredensialnya benar.")