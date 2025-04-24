import os
import pandas as pd
from datetime import datetime
import requests
import matplotlib.pyplot as plt

# === CONFIG ===
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CSV_FILE = "scalping_trades_log.csv"
IMG_FILE = "pnl_graph.png"

# === LOAD DATA ===
if not os.path.exists(CSV_FILE):
    print("❌ Aucun fichier CSV trouvé.")
    exit()

df = pd.read_csv(CSV_FILE)
df["Date"] = pd.to_datetime(df["Date"])
today = datetime.now().date()
today_trades = df[df["Date"].dt.date == today]

if today_trades.empty:
    message = f"📊 Aucun trade effectué le {today.strftime('%d/%m/%Y')}."
else:
    total = len(today_trades)
    pnl = today_trades["PnL%"].sum()
    winrate = len(today_trades[today_trades["PnL%"] > 0]) / total * 100

    # === GENERATE PNL GRAPH ===
    today_trades["PnL Cumulé"] = today_trades["PnL%"].cumsum()
    plt.figure(figsize=(10, 5))
    plt.plot(today_trades["Date"], today_trades["PnL Cumulé"], marker='o', label="PnL Cumulé")
    plt.title("📈 PnL du jour")
    plt.xlabel("Heure")
    plt.ylabel("PnL (%)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(IMG_FILE)

    # === MESSAGE TEXTE ===
    message = f"""📊 Rapport du {today.strftime('%d/%m/%Y')} :

• Nombre de trades : {total}
• Winrate : {winrate:.1f}%
• PnL total : {pnl:.2f} %
"""

# === ENVOI MESSAGE + PHOTO
url_text = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
url_photo = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

# Texte
requests.post(url_text, data={"chat_id": CHAT_ID, "text": message})

# Image si dispo
if os.path.exists(IMG_FILE):
    with open(IMG_FILE, "rb") as photo:
        requests.post(url_photo, files={"photo": photo}, data={"chat_id": CHAT_ID})
