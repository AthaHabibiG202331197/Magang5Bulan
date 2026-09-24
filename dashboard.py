import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Mengatur tampilan halaman web
st.set_page_config(page_title="Dashboard IT Enterprise", layout="wide")

st.title("📊 Dashboard Analisis Berita IT & Cyber Security")
st.markdown("Visualisasi otomatis dari hasil scraping Bisnis.com & CNBC")

# Fungsi untuk menarik data dari PostgreSQL (disimpan di cache agar super cepat)
@st.cache_data
def load_data():
    # PENTING: Ganti 'password_kamu' dengan password PostgreSQL Docker-mu
    engine = create_engine('postgresql://postgres:a05h07g04@localhost:5432/postgres')
    df = pd.read_sql_table('insight_it_enterprise', con=engine)
    return df

try:
    # Memuat data
    df = load_data()

    # 1. Menampilkan Metrik Utama (Total Artikel)
    st.metric(label="Total Artikel Terkumpul", value=f"{len(df)} Berita")
    st.divider()

    # 2. Membuat tabel agregasi Fokus Teknologi
    sebaran_teknologi = df['Fokus Teknologi'].value_counts().reset_index()
    sebaran_teknologi.columns = ['Kategori', 'Jumlah Artikel']

    st.subheader("Sebaran Artikel Berdasarkan Fokus Teknologi")
    
    # Membagi layar jadi 2 kolom (Kiri: Grafik, Kanan: Tabel)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Menampilkan Bar Chart (Otomatis interaktif)
        st.bar_chart(data=df['Fokus Teknologi'].value_counts())
        
    with col2:
        # Menampilkan tabel ringkasan
        st.dataframe(sebaran_teknologi, use_container_width=True)

    st.divider()

    # 3. Menampilkan Data Mentah yang bisa di-scroll dan difilter
    with st.expander("🔎 Klik untuk melihat Data Mentah Lengkap"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Gagal terhubung ke database. Error: {e}")
    st.info("Tips: Pastikan container PostgreSQL di Docker Desktop sedang menyala/Running.")