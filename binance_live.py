# binance_live.py
import os
from dotenv import load_dotenv
from binance.client import Client

# Charger les variables d'environnement
load_dotenv()

# === CONFIGURATION ===
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError("Clés API Binance non trouvées. Vérifie ton fichier .env.")

# Créer l'objet client Binance
client = Client(API_KEY, API_SECRET)

# === PAPER TRADING ===
paper_trading = True
fake_cash = 10000
fake_holdings = {}

def execute_trade(symbol, side, quantity, use_market=True):
    global fake_cash, fake_holdings

    price = float(client.get_symbol_ticker(symbol=symbol)["price"])
    if paper_trading:
        if side == "BUY":
            cost = quantity * price
            if fake_cash >= cost:
                fake_cash -= cost
                fake_holdings[symbol] = fake_holdings.get(symbol, 0) + quantity
                print(f"[PAPER] BUY {quantity} {symbol} @ {price:.2f} | Cash: {fake_cash:.2f}")
            else:
                print("[PAPER] Fonds insuffisants.")
        elif side == "SELL":
            held = fake_holdings.get(symbol, 0)
            if held >= quantity:
                fake_cash += quantity * price
                fake_holdings[symbol] -= quantity
                print(f"[PAPER] SELL {quantity} {symbol} @ {price:.2f} | Cash: {fake_cash:.2f}")
            else:
                print("[PAPER] Pas assez pour vendre.")
        return True

    # Live mode
    try:
        order_type = Client.ORDER_TYPE_MARKET if use_market else Client.ORDER_TYPE_LIMIT
        order = client.create_order(
            symbol=symbol,
            side=Client.SIDE_BUY if side == "BUY" else Client.SIDE_SELL,
            type=order_type,
            quantity=quantity
        )
        print(f"[LIVE] Order exécuté : {order}")
        return order
    except Exception as e:
        print(f"❌ Erreur d'ordre : {e}")
        return None

def get_balance():
    if paper_trading:
        return fake_cash, fake_holdings
    balances = client.get_account()["balances"]
    return {b["asset"]: float(b["free"]) for b in balances if float(b["free"]) > 0}
