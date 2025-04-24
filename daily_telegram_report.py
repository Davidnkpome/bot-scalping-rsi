import os
import pandas as pd
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

df = pd.read_csv("scalping_trades_log.csv")
df["Date"] = pd.to_datetime(df["Date"])
today = datetime.now().date()
today_trades = df[df["Date"].dt.date == today]

if today_trades.empty:
    message = "📊 Aucun trade effectué aujourd'hui."
else:
    total = len(today_trades)
    pnl = today_trades["PnL%"].sum()
    winrate = len(today_trades[today_trades["PnL%"] > 0]) / total * 100
    message = f"""📊 Rapport du {today.strftime('%d/%m/%Y')} :

• Nombre de trades : {total}
• Winrate : {winrate:.1f}%
• PnL total : {pnl:.2f} %
"""

requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": message})
