# scalping_stats_dashboard.py
import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("📊 Dashboard de trading - Scalping RSI + MACD")

log_file = "scalping_trades_log.csv"

if not os.path.exists(log_file):
    st.warning("Aucun fichier de log trouvé. Lance le bot pour générer les premiers trades.")
else:
    df = pd.read_csv(log_file)
    df["Date"] = pd.to_datetime(df["Date"])

    st.subheader("🧾 Dernières transactions")
    st.dataframe(df[::-1], use_container_width=True)

    total_trades = len(df)
    wins = df[df["PnL%"] > 0].shape[0]
    losses = df[df["PnL%"] <= 0].shape[0]
    winrate = (wins / total_trades) * 100 if total_trades else 0
    cumulated_return = df["PnL%"].cumsum()

    col1, col2, col3 = st.columns(3)
    col1.metric("🔁 Total trades", total_trades)
    col2.metric("🥇 Winrate", f"{winrate:.2f} %")
    col3.metric("📈 PnL cumulé (%)", f"{cumulated_return.iloc[-1]:.2f} %")

    st.subheader("📉 Évolution du PnL cumulé")
    st.line_chart(cumulated_return)

    st.subheader("📊 Répartition des actions")
    st.bar_chart(df["Action"].value_counts())
