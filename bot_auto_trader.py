# bot_auto_trader.py
import time
import pandas as pd
import ta
import datetime
import csv
import os
import requests
from cleanup_old_logs import clean_old_logs
from binance_live import execute_trade, paper_trading
from binance.client import Client
from dotenv import load_dotenv

# === INIT ===
load_dotenv()
clean_old_logs()  # Nettoyage automatique au lancement

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbol = "BTCUSDT"
timeframe = Client.KLINE_INTERVAL_1MINUTE
rsi_period = 14
rsi_buy = 30
rsi_sell = 70
qty = 0.001
interval = 60

take_profit_pct = 0.005
stop_loss_pct = 0.002

entry_price = None
in_position = False

LOG_FILE = "scalping_trades_log.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Action", "Prix", "RSI", "MACD", "Signal", "PnL%"])

def notify_telegram(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
        except:
            print("❌ Notification Telegram échouée")

print("🚀 Bot SCALPING PRO (RSI + MACD + TP/SL) - LIVE")

while True:
    try:
        klines = client.get_klines(symbol=symbol, interval=timeframe, limit=100)
        df = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "qav", "trades", "tb_base", "tb_quote", "ignore"])
        df["close"] = pd.to_numeric(df["close"])

        rsi = ta.momentum.RSIIndicator(df["close"], window=rsi_period)
        macd = ta.trend.MACD(df["close"])
        df["RSI"] = rsi.rsi()
        df["MACD"] = macd.macd()
        df["MACD_signal"] = macd.macd_signal()

        latest_rsi = df["RSI"].iloc[-1]
        macd_now = df["MACD"].iloc[-1]
        signal_now = df["MACD_signal"].iloc[-1]
        price_now = df["close"].iloc[-1]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{now}] Prix: {price_now:.2f} | RSI: {latest_rsi:.2f} | MACD: {macd_now:.4f} | Signal: {signal_now:.4f}")

        action = None
        pnl = 0

        if not in_position:
            if latest_rsi < rsi_buy and macd_now > signal_now:
                action = "BUY"
                execute_trade(symbol, action, qty)
                entry_price = price_now
                in_position = True
        else:
            pnl = (price_now - entry_price) / entry_price
            if pnl >= take_profit_pct:
                action = "TP SELL"
                execute_trade(symbol, "SELL", qty)
                in_position = False
            elif pnl <= -stop_loss_pct:
                action = "SL SELL"
                execute_trade(symbol, "SELL", qty)
                in_position = False
            elif latest_rsi > rsi_sell and macd_now < signal_now:
                action = "RSI+MACD SELL"
                execute_trade(symbol, "SELL", qty)
                in_position = False

        if action:
            if "FAIL" not in action:  # log only executed trades
                with open(LOG_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([now, action, round(price_now, 2), round(latest_rsi, 2), round(macd_now, 4), round(signal_now, 4), round(pnl*100, 2)])
                notify_telegram(f"{now} - {action} {symbol} @ {price_now:.2f} | RSI: {latest_rsi:.1f} | MACD: {macd_now:.4f}")

    except Exception as e:
        print(f"❌ Erreur bot : {e}")

    time.sleep(interval)