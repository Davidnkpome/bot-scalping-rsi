import yfinance as yf
import pandas as pd
import ta

def run_backtest(ticker, start_date, end_date, capital, ma_short, ma_long, take_profit, stop_loss, strategy="MA Crossover"):
    data = yf.download(ticker, start=start_date, end=end_date)
    data.dropna(inplace=True)

    # === Indicateurs techniques ===
    data["MA_Short"] = data["Close"].rolling(ma_short).mean()
    data["MA_Long"] = data["Close"].rolling(ma_long).mean()

    # 🔧 Forcer close en série 1D propre
    close_series = data["Close"]
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.squeeze()

    data["RSI"] = ta.momentum.RSIIndicator(close=close_series, window=14).rsi()
    macd = ta.trend.MACD(close=close_series)
    data["MACD"] = macd.macd()
    data["MACD_signal"] = macd.macd_signal()
    bb = ta.volatility.BollingerBands(close=close_series, window=20, window_dev=2)
    data["BB_upper"] = bb.bollinger_hband()
    data["BB_lower"] = bb.bollinger_lband()

    # === Signaux ===
    signals = []
    for i in range(len(data)):
        signal = 0
        if strategy == "MA Crossover":
            if i >= ma_long:
                if data["MA_Short"].iloc[i] > data["MA_Long"].iloc[i] and data["MA_Short"].iloc[i-1] <= data["MA_Long"].iloc[i-1]:
                    signal = 1
                elif data["MA_Short"].iloc[i] < data["MA_Long"].iloc[i] and data["MA_Short"].iloc[i-1] >= data["MA_Long"].iloc[i-1]:
                    signal = -1
        elif strategy == "RSI":
            if data["RSI"].iloc[i] < 30:
                signal = 1
            elif data["RSI"].iloc[i] > 70:
                signal = -1
        elif strategy == "MACD":
            if data["MACD"].iloc[i] > data["MACD_signal"].iloc[i] and data["MACD"].iloc[i-1] <= data["MACD_signal"].iloc[i-1]:
                signal = 1
            elif data["MACD"].iloc[i] < data["MACD_signal"].iloc[i] and data["MACD"].iloc[i-1] >= data["MACD_signal"].iloc[i-1]:
                signal = -1
        elif strategy == "Bollinger":
            if data["Close"].iloc[i] < data["BB_lower"].iloc[i]:
                signal = 1
            elif data["Close"].iloc[i] > data["BB_upper"].iloc[i]:
                signal = -1
        signals.append(signal)

    data["Signal"] = signals

    # === Backtest ===
    shares = 0
    cash = capital
    in_position = False
    entry_price = 0
    portfolio_values = []
    trade_log = []
    nb_win = 0
    nb_lose = 0

    for i in range(len(data)):
        date = data.index[i].strftime("%Y-%m-%d")
        price = float(data["Close"].iloc[i])
        signal = data["Signal"].iloc[i]
        total_value = cash + shares * price

        if in_position:
            pnl_pct = (price - entry_price) / entry_price
            if pnl_pct >= take_profit or pnl_pct <= -stop_loss:
                cash = shares * price
                profit = price - entry_price
                if profit > 0: nb_win += 1
                else: nb_lose += 1
                trade_log.append(["TP/SL", date, round(price, 2), round(shares, 6), round(cash, 2), round(total_value, 2)])
                shares = 0
                in_position = False

        if signal == 1 and not in_position:
            shares = cash / price
            entry_price = price
            cash = 0
            trade_log.append(["Achat", date, round(price, 2), round(shares, 6), round(entry_price * shares, 2), round(total_value, 2)])
            in_position = True

        elif signal == -1 and in_position:
            cash = shares * price
            profit = price - entry_price
            if profit > 0: nb_win += 1
            else: nb_lose += 1
            trade_log.append(["Vente", date, round(price, 2), round(shares, 6), round(cash, 2), round(total_value, 2)])
            shares = 0
            in_position = False

        portfolio_values.append(cash + shares * price)

    data["Portfolio"] = portfolio_values
    final_value = data["Portfolio"].iloc[-1]
    net_profit = final_value - capital
    percent_return = (net_profit / capital) * 100
    total_trades = nb_win + nb_lose
    winrate = (nb_win / total_trades * 100) if total_trades else 0

    return {
        "data": data,
        "trades": trade_log,
        "final_value": round(final_value, 2),
        "net_profit": round(net_profit, 2),
        "percent_return": round(percent_return, 2),
        "total_trades": total_trades,
        "winrate": round(winrate, 2),
        "nb_win": nb_win,
        "nb_lose": nb_lose
    }