# portfolio_dashboard.py
import streamlit as st
from binance_live import get_balance, execute_trade, paper_trading
import time
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 Portfolio Binance - Mode " + ("Virtuel" if paper_trading else "Réel"))

# === AUTHENTIFICATION POUR TRADING RÉEL ===
auth_ok = True
if not paper_trading:
    password = st.text_input("🔐 Entrez le mot de passe pour autoriser le trading :", type="password")
    auth_ok = (password == "secure123")
    if not auth_ok:
        st.warning("Accès refusé au mode trading réel.")

refresh_interval = st.slider("⏱️ Rafraîchissement automatique (secondes)", 5, 60, 10)

# === Formulaire Buy/Sell ===
st.subheader("📥 Exécuter un ordre")
col1, col2, col3, col4 = st.columns(4)
with col1:
    symbol = st.text_input("Ticker (ex: BTCUSDT)", "BTCUSDT")
with col2:
    side = st.selectbox("Sens", ["BUY", "SELL"])
with col3:
    qty = st.number_input("Quantité", min_value=0.0001, value=0.001)
with col4:
    trigger = st.button("Envoyer l'ordre")

# Historique local (simulation)
if "history" not in st.session_state:
    st.session_state.history = []

if trigger and auth_ok:
    result = execute_trade(symbol, side, qty)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append({"Date": now, "Type": side, "Ticker": symbol, "Quantité": qty})
    st.success("Ordre envoyé !" if result else "Erreur lors de l'envoi")

# === Affichage de l'historique ===
st.subheader("🧾 Historique des ordres")
if st.session_state.history:
    st.dataframe(st.session_state.history[::-1])
else:
    st.info("Aucun ordre exécuté pour l'instant.")

# === PORTFOLIO ===
st.subheader("📈 Portefeuille")
placeholder = st.empty()
last_balance = 0

def get_total_value(data):
    if isinstance(data, dict):
        return sum(data.values())
    return float(data) if isinstance(data, (int, float)) else 0

for i in range(1000):
    with placeholder.container():
        cash, holdings = get_balance()
        total_now = get_total_value(cash) + sum(holdings.values()) if isinstance(holdings, dict) else 0

        if paper_trading:
            st.metric("💰 Cash virtuel", f"{cash:.2f} $")
            st.write("### 📦 Holdings simulés")
            if holdings:
                st.bar_chart({"Quantité": holdings})
            else:
                st.info("Aucune position ouverte.")
        else:
            st.write("### 📦 Solde réel Binance")
            if isinstance(cash, dict):
                st.bar_chart({"Quantité": cash})
            else:
                st.warning("Erreur de récupération du solde.")

        if i > 0:
            diff = total_now - last_balance
            if abs(diff) > 10:
                st.warning(f"🔔 Variation de portefeuille : {'+' if diff > 0 else ''}{diff:.2f} $")

        last_balance = total_now

    time.sleep(refresh_interval)