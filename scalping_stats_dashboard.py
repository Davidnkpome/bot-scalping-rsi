import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os

# === CONFIG VISUELLE ===
st.set_page_config(
    page_title="💹 Bot Scalping Dashboard",
    page_icon="📈",
    layout="wide"
)

# === AUTHENTIFICATION ===
PASSWORD = "trading2025"  # ✅ Change ce mot de passe ici

def login():
    with st.sidebar:
        st.title("🔐 Connexion")
        pw = st.text_input("Mot de passe", type="password")
        if pw != PASSWORD:
            st.warning("Mot de passe incorrect.")
            st.stop()
login()

# === TITRE ===
st.title("📊 Tableau de bord - Scalping RSI + MACD")

LOG_FILE = "scalping_trades_log.csv"

if not os.path.exists(LOG_FILE):
    st.warning("Aucun trade trouvé. Le fichier de log n'existe pas encore.")
    st.stop()

# === CHARGEMENT DATA ===
df = pd.read_csv(LOG_FILE)
df["Date"] = pd.to_datetime(df["Date"])
df.dropna(subset=["Prix"], inplace=True)
df["PnL%"] = df["PnL%"].fillna(0)
df["PnL Cumulé"] = df["PnL%"].cumsum()

# === STATISTIQUES ===
total_trades = len(df)
win_trades = df[df["PnL%"] > 0]
lose_trades = df[df["PnL%"] < 0]
winrate = len(win_trades) / total_trades * 100 if total_trades else 0
total_pnl = df["PnL%"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💼 Total Trades", total_trades)
col2.metric("🥇 Winrate", f"{winrate:.2f} %")
col3.metric("📈 PnL Cumulé", f"{total_pnl:.2f} %")

st.markdown("---")

# === STATS JOURNALIÈRES ===
st.subheader("📅 Statistiques Journalières")
df["Jour"] = df["Date"].dt.date
daily_stats = df.groupby("Jour").agg({
    "PnL%": "sum",
    "Date": "count"
}).rename(columns={"PnL%": "PnL Jour", "Date": "Nb Trades"}).reset_index()

st.dataframe(daily_stats, use_container_width=True)


# === GRAPHE PNL ===
st.subheader("📈 Performance du Bot")
fig, ax = plt.subplots()
ax.plot(df["Date"], df["PnL Cumulé"], label="PnL Cumulé", linewidth=2)
ax.set_xlabel("Date")
ax.set_ylabel("PnL (%)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# === TABLEAU DES TRADES ===
st.subheader("🧾 Détail des trades")
st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)

# === EXPORT CSV ===
st.download_button("📥 Télécharger CSV", data=df.to_csv(index=False), file_name="trades_export.csv")
