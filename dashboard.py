from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Warna dashboard
bg = "#0A1931"
panel = "#13264D"
biru = "#4DA8DA"
oranye = "#FFB347"
merah = "#FF6B6B"
putih = "#EAF0FA"

sns.set_theme(
    style="darkgrid",
    rc={
        "figure.facecolor": bg,
        "axes.facecolor": panel,
        "axes.labelcolor": putih,
        "axes.titlecolor": putih,
        "xtick.color": putih,
        "ytick.color": putih,
        "text.color": putih,
        "grid.color": "#2A3F6B"
    }
)

st.markdown(f"""
<style>
.stApp, [data-testid="stHeader"] {{
    background-color: {bg};
}}
[data-testid="stSidebar"] {{
    background-color: {panel};
}}
.stApp h1, .stApp h2, .stApp h3, .stApp p,
.stApp label, [data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {{
    color: {putih};
}}
</style>
""", unsafe_allow_html=True)

# Membaca data
folder = Path(__file__).parent

@st.cache_data
def baca_data():
    jam = pd.read_csv(folder / "main_data.csv")
    harian = pd.read_csv(folder / "daily_data.csv")

    jam["dteday"] = pd.to_datetime(jam["dteday"])
    harian["dteday"] = pd.to_datetime(harian["dteday"])

    return jam, harian


df_jam, df_harian = baca_data()

# Menyiapkan nama kategori jika belum ada
nama_musim = {
    1: "Musim Semi",
    2: "Musim Panas",
    3: "Musim Gugur",
    4: "Musim Dingin"
}

nama_cuaca = {
    1: "Cerah",
    2: "Berawan/Berkabut",
    3: "Hujan/Salju Ringan",
    4: "Hujan/Salju Lebat"
}

if "season_label" not in df_harian.columns:
    df_harian["season_label"] = df_harian["season"].map(nama_musim)

if "season_label" not in df_jam.columns:
    df_jam["season_label"] = df_jam["season"].map(nama_musim)

if "day_type" not in df_harian.columns:
    df_harian["day_type"] = df_harian["workingday"].map({
        1: "Hari Kerja",
        0: "Hari Non-Kerja"
    })

if "day_type" not in df_jam.columns:
    df_jam["day_type"] = df_jam["workingday"].map({
        1: "Hari Kerja",
        0: "Hari Non-Kerja"
    })

if "weather_label" not in df_harian.columns:
    df_harian["weather_label"] = df_harian["weathersit"].map(nama_cuaca)

# Filter di sidebar
with st.sidebar:
    st.title("🚲 Bike Sharing")
    st.write("Dashboard penyewaan sepeda tahun 2011–2012")

    tanggal_awal = df_harian["dteday"].min().date()
    tanggal_akhir = df_harian["dteday"].max().date()

    tanggal = st.date_input(
        "Pilih rentang tanggal",
        value=(tanggal_awal, tanggal_akhir),
        min_value=tanggal_awal,
        max_value=tanggal_akhir
    )

    pilihan_musim = [
    "Musim Semi",
    "Musim Panas",
    "Musim Gugur",
    "Musim Dingin"
    ]

    musim = st.multiselect(
        "Pilih musim",
        pilihan_musim,
        default=pilihan_musim
    )

if isinstance(tanggal, (tuple, list)):
    if len(tanggal) == 2:
        mulai, selesai = tanggal
    elif len(tanggal) == 1:
        mulai = selesai = tanggal[0]
    else:
        mulai, selesai = tanggal_awal, tanggal_akhir
else:
    mulai = selesai = tanggal

# Menerapkan filter
jam = df_jam[
    (df_jam["dteday"] >= pd.Timestamp(mulai)) &
    (df_jam["dteday"] <= pd.Timestamp(selesai)) &
    (df_jam["season_label"].isin(musim))
].copy()

harian = df_harian[
    (df_harian["dteday"] >= pd.Timestamp(mulai)) &
    (df_harian["dteday"] <= pd.Timestamp(selesai)) &
    (df_harian["season_label"].isin(musim))
].copy()

# Judul dashboard
st.title("🚲 Dashboard Analisis Bike Sharing")
st.write(
    "Pola penyewaan sepeda berdasarkan jam, "
    "jenis hari, dan kondisi cuaca."
)

if jam.empty or harian.empty:
    st.warning("Data tidak ditemukan. Coba ubah filter tanggal atau musim.")
    st.stop()

# Informasi utama
jam_tertinggi = jam.groupby("hr")["cnt"].mean().idxmax()
total = harian["cnt"].sum()

kol1, kol2, kol3, kol4 = st.columns(4)

kol1.metric("Total Penyewaan", f"{total:,.0f}")
kol2.metric("Rata-rata per Hari", f"{harian['cnt'].mean():,.0f}")
kol3.metric(
    "Proporsi Registered",
    f"{harian['registered'].sum() / total:.1%}"
)
kol4.metric("Jam Tersibuk", f"{int(jam_tertinggi):02d}.00")

tab1, tab2, tab3 = st.tabs([
    "⏰ Pola per Jam",
    "📅 Hari Kerja vs Non-Kerja",
    "🌦️ Kondisi Cuaca"
])

# Pola penyewaan per jam
with tab1:
    st.subheader("Pola Penyewaan Sepeda Berdasarkan Jam")

    pilihan = st.radio(
        "Jenis pengguna",
        ["Semua", "Registered", "Casual"],
        horizontal=True
    )

    kolom = {
        "Semua": "cnt",
        "Registered": "registered",
        "Casual": "casual"
    }

    data_jam = jam.groupby("hr")[kolom[pilihan]].mean()
    tiga_tertinggi = data_jam.nlargest(3)

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        data_jam.index,
        data_jam.values,
        marker="o",
        color=biru
    )

    ax.scatter(
        tiga_tertinggi.index,
        tiga_tertinggi.values,
        color=merah,
        s=90,
        label="3 jam tertinggi"
    )

    for x, y in tiga_tertinggi.items():
        ax.annotate(
            f"{y:.0f}",
            (x, y),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center"
        )

    ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Jam")
    ax.set_xlabel("Jam")
    ax.set_ylabel("Rata-rata Penyewaan")
    ax.set_xticks(range(24))
    ax.legend()

    st.pyplot(fig)
    plt.close(fig)

    jam_sepi = int(data_jam.idxmin())
    jam_puncak = ", ".join(
        f"{int(x):02d}.00" for x in tiga_tertinggi.index
    )

    st.info(
        f"Penyewaan tertinggi terjadi pada pukul {jam_puncak}. "
        f"Sementara itu, penyewaan terendah terjadi pada pukul "
        f"{jam_sepi:02d}.00."
    )

# Hari kerja dan hari libur
with tab2:
    st.subheader("Perbandingan Hari Kerja dan Hari Non-Kerja")

    rata_hari = harian.groupby("day_type")["cnt"].mean()
    pola_hari = jam.groupby(["hr", "day_type"])["cnt"].mean().reset_index()

    kiri, kanan = st.columns([1, 2])

    with kiri:
        fig, ax = plt.subplots(figsize=(5, 5))

        urutan = ["Hari Kerja", "Hari Non-Kerja"]
        data_hari = rata_hari.reindex(urutan).dropna()

        ax.bar(
            data_hari.index,
            data_hari.values,
            color=[biru, oranye][:len(data_hari)]
        )

        for i, nilai in enumerate(data_hari.values):
            ax.text(i, nilai + 40, f"{nilai:,.0f}", ha="center")

        ax.set_title("Rata-rata Penyewaan Harian")
        ax.set_ylabel("Jumlah Penyewaan")
        ax.tick_params(axis="x", rotation=10)

        st.pyplot(fig)
        plt.close(fig)

    with kanan:
        fig, ax = plt.subplots(figsize=(9, 5))

        sns.lineplot(
            data=pola_hari,
            x="hr",
            y="cnt",
            hue="day_type",
            marker="o",
            palette={
                "Hari Kerja": biru,
                "Hari Non-Kerja": oranye
                },
            ax=ax
        )

        ax.set_title("Pola Penyewaan Berdasarkan Jam")
        ax.set_xlabel("Jam")
        ax.set_ylabel("Rata-rata Penyewaan")
        ax.set_xticks(range(24))

        st.pyplot(fig)
        plt.close(fig)

if len(data_hari) == 2:
    selisih = data_hari["Hari Kerja"] - data_hari["Hari Non-Kerja"]
    persen = abs(selisih) / data_hari["Hari Non-Kerja"] * 100

    if selisih >= 0:
        hasil = f"lebih tinggi {persen:.1f}%"
    else:
        hasil = f"lebih rendah {persen:.1f}%"

    st.info(
        f"Rata-rata penyewaan pada hari kerja {hasil} "
        f"dibandingkan hari non-kerja."
    )

# Kondisi cuaca
with tab3:
    st.subheader("Penyewaan Sepeda Berdasarkan Kondisi Cuaca")

    jam["weathersit"] = pd.to_numeric(
        jam["weathersit"], errors="coerce"
    )

    jam["cnt"] = pd.to_numeric(
        jam["cnt"], errors="coerce"
    )

    urutan_cuaca = [
        "Cerah",
        "Berkabut/Mendung",
        "Hujan/Salju Ringan",
        "Hujan/Salju Lebat"
    ]

    rata_cuaca = (
        jam.dropna(subset=["weathersit", "cnt"])
        .groupby("weathersit")["cnt"]
        .mean()
        .reindex([1, 2, 3, 4])
        .dropna()
    )

    rata_cuaca.index = rata_cuaca.index.map(nama_cuaca)

    if not rata_cuaca.empty:
        fig, ax = plt.subplots(figsize=(10, 5))

        warna = [
            biru if cuaca == "Cerah" else "#6B7A99"
            for cuaca in rata_cuaca.index
        ]

        ax.bar(
            rata_cuaca.index,
            rata_cuaca.values,
            color=warna
        )

        for i, nilai in enumerate(rata_cuaca.values):
            ax.text(
                i,
                nilai + (rata_cuaca.max() * 0.02),
                f"{nilai:,.2f}",
                ha="center"
            )

        ax.set_title("Rata-rata Penyewaan Sepeda per Jam berdasarkan Kondisi Cuaca")
        ax.set_xlabel("Kondisi Cuaca")
        ax.set_ylabel("Rata-rata Penyewaan per Jam (sepeda)")

        ax.set_ylim(0, rata_cuaca.max() * 1.15)

        plt.xticks(rotation=10)
        st.pyplot(fig)
        plt.close(fig)

        if "Cerah" in rata_cuaca.index and len(rata_cuaca) > 1:
            cuaca_terendah = rata_cuaca.idxmin()
            nilai_cerah = rata_cuaca["Cerah"]

            penurunan = (
                1 - rata_cuaca.min() / nilai_cerah
            ) * 100

            st.info(
                f"Rata-rata penyewaan pada kondisi "
                f"{cuaca_terendah} lebih rendah sekitar "
                f"{penurunan:.1f}% dibandingkan saat cuaca cerah."
            )

        with st.expander(
            "Lihat rata-rata penyewaan setiap kondisi cuaca"
        ):
            st.dataframe(
                rata_cuaca.round(2).rename(
                    "Rata-rata Penyewaan"
                )
            )

    else:
        st.warning("Tidak ada data cuaca yang valid untuk ditampilkan.")

st.caption("Sumber: Bike Sharing Dataset (2011–2012)")