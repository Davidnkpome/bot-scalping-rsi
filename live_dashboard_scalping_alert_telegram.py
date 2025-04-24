import streamlit as st
import pandas as pd
import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LOG_FILE = "scalping_rsi_bollinger_log.csv"

st.set_page_config(page_title="📊 Scalping Live - RSI + Bollinger", page_icon="📈", layout="wide")
st.title("📊 Dashboard LIVE + Alerte Telegram - Scalping RSI + Bollinger")

placeholder = st.empty()
last_trade_count = 0

def send_telegram_alert(row):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        msg = (
            f"📥 *Nouveau trade détecté !*\n"
            f"Pair: {row['Symbole']}\n"
            f"Action: {row['Action']}\n"
            f"Prix: {row['Prix']}\n"
            f"RSI: {row['RSI']} | Bollinger: [{row['Bollinger_Low']} - {row['Bollinger_Up']}]"
        )
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"},
                timeout=5
            )
        except:
            st.warning("❌ Envoi Telegram échoué.")

sound_alert = '''
<script>
function playBeep() {
    const beep = new Audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg");
    beep.play();
}
playBeep();
</script>
'''

if not os.path.exists(LOG_FILE):
    st.warning("Aucun fichier de log détecté pour le moment.")
    st.stop()

while True:
    with placeholder.container():
        df = pd.read_csv(LOG_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        total_trades = len(df)
        new_trade_detected = total_trades > last_trade_count

        # Stat global
        pnl_total = df["PnL%"].sum()
        winrate = len(df[df["PnL%"] > 0]) / total_trades * 100 if total_trades > 0 else 0

        st.subheader("📊 Statistiques Globales")
        col1, col2, col3 = st.columns(3)
        col1.metric("📈 PnL Total", f"{pnl_total:.2f} %")
        col2.metric("💼 Total Trades", total_trades)
        col3.metric("🥇 Winrate", f"{winrate:.2f} %")

        st.markdown("### 🔍 Détail par Crypto")
        grouped = df.groupby("Symbole").agg(
            Total=("Symbole", "count"),
            PnL=("PnL%", "sum"),
            Dernier_Prix=("Prix", "last")
        ).reset_index()
        st.dataframe(grouped, use_container_width=True)

        st.markdown("### 📋 Derniers Trades")
        st.dataframe(df.sort_values("Date", ascending=False).head(10), use_container_width=True)

        # ALERTE
        if new_trade_detected:
            last_trade = df.iloc[-1]
            st.success(f"💥 Nouveau trade : {last_trade['Action']} {last_trade['Symbole']} @ {last_trade['Prix']}", icon="⚡")
            st.components.v1.html(sound_alert)
            send_telegram_alert(last_trade)
            last_trade_count = total_trades

    time.sleep(10)
