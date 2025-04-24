
import os
import time
import csv
import requests
import threading
import datetime
import pandas as pd
import ta
from dotenv import load_dotenv
from binance.client import Client
from binance_live import paper_trading
from cleanup_old_logs import clean_old_logs
from healthcheck import PingHandler, HTTPServer

# === PARAMÈTRES ===
REAL_MODE = False
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOGEUSDT"]
TIMEFRAME = Client.KLINE_INTERVAL_1MINUTE
RSI_PERIOD = 14
INTERVAL = 60
TP_PCT = 0.005
SL_PCT = 0.003
LOG_FILE = "scalping_rsi_bollinger_log.csv"

# === INIT ===
load_dotenv()
clean_old_logs()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
client = Client(API_KEY, API_SECRET)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Symbole", "Action", "Prix", "RSI", "Bollinger_Low", "Bollinger_Up", "PnL%"])

positions = {}

def notify_telegram(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                          data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
        except:
            print("❌ Erreur Telegram")

def start_healthcheck_server():
    server = HTTPServer(('', 8080), PingHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

start_healthcheck_server()
print("🚀 Bot RSI + Bollinger lancé... (virtuel)")

while True:
    for symbol in SYMBOLS:
        try:
            klines = client.get_klines(symbol=symbol, interval=TIMEFRAME, limit=100)
            df = pd.DataFrame(klines, columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "qav", "trades", "tb_base", "tb_quote", "ignore"
            ])
            df["close"] = pd.to_numeric(df["close"])

            rsi = ta.momentum.RSIIndicator(df["close"], window=RSI_PERIOD).rsi()
            bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
            df["RSI"] = rsi
            df["BB_lower"] = bb.bollinger_lband()
            df["BB_upper"] = bb.bollinger_hband()

            price = df["close"].iloc[-1]
            rsi_val = df["RSI"].iloc[-1]
            bb_low = df["BB_lower"].iloc[-1]
            bb_up = df["BB_upper"].iloc[-1]
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            action = None
            pnl = 0

            in_position = symbol in positions

            if not in_position:
                if rsi_val < 30 and price < bb_low:
                    action = "BUY"
                    positions[symbol] = price
                    paper_trading(symbol, "BUY", 0.001)
            else:
                entry = positions[symbol]
                pnl = (price - entry) / entry
                if pnl >= TP_PCT:
                    action = "TP SELL"
                    del positions[symbol]
                    paper_trading(symbol, "SELL", 0.001)
                elif pnl <= -SL_PCT:
                    action = "SL SELL"
                    del positions[symbol]
                    paper_trading(symbol, "SELL", 0.001)
                elif rsi_val > 70 and price > bb_up:
                    action = "RSI+BOLL SELL"
                    del positions[symbol]
                    paper_trading(symbol, "SELL", 0.001)

            if action:
                with open(LOG_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([now, symbol, action, round(price, 2), round(rsi_val, 2), round(bb_low, 2), round(bb_up, 2), round(pnl * 100, 2)])
                notify_telegram(f"{now} - {action} {symbol} @ {price:.2f} | RSI: {rsi_val:.1f}")

        except Exception as e:
            print(f"❌ [{symbol}] Erreur : {e}")

    time.sleep(INTERVAL)
