# optimizer.py
from core_bot import run_backtest
import numpy as np
import pandas as pd

def optimize_strategy(ticker, start_date, end_date, strategy="MA Crossover", capital=10000):
    best_config = None
    best_return = -999999
    results = []

    for ma_short in [10, 15, 20]:
        for ma_long in [30, 50, 100]:
            if ma_short >= ma_long:
                continue
            for tp in [0.05, 0.1, 0.2]:
                for sl in [0.03, 0.05, 0.1]:
                    result = run_backtest(
                        ticker=ticker,
                        start_date=start_date,
                        end_date=end_date,
                        capital=capital,
                        ma_short=ma_short,
                        ma_long=ma_long,
                        take_profit=tp,
                        stop_loss=sl,
                        strategy=strategy
                    )
                    results.append({
                        "Strategy": strategy,
                        "MA_Short": ma_short,
                        "MA_Long": ma_long,
                        "TP": tp,
                        "SL": sl,
                        "Return%": result["percent_return"],
                        "Winrate": result["winrate"],
                        "Trades": result["total_trades"]
                    })

                    if result["percent_return"] > best_return:
                        best_return = result["percent_return"]
                        best_config = results[-1]

    df = pd.DataFrame(results)
    return best_config, df

def compare_strategies(ticker, start_date, end_date, capital=10000, ma_short=20, ma_long=50, tp=0.1, sl=0.05):
    strategies = ["MA Crossover", "RSI", "MACD", "Bollinger"]
    results = []
    for strat in strategies:
        result = run_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            capital=capital,
            ma_short=ma_short,
            ma_long=ma_long,
            take_profit=tp,
            stop_loss=sl,
            strategy=strat
        )
        results.append({
            "Strategy": strat,
            "Return%": result["percent_return"],
            "Winrate": result["winrate"],
            "Trades": result["total_trades"]
        })
    return pd.DataFrame(results)

def multi_crypto_backtest(tickers, start_date, end_date, strategy="MA Crossover", capital=10000, ma_short=20, ma_long=50, tp=0.1, sl=0.05):
    results = []
    for ticker in tickers:
        result = run_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            capital=capital,
            ma_short=ma_short,
            ma_long=ma_long,
            take_profit=tp,
            stop_loss=sl,
            strategy=strategy
        )
        results.append({
            "Ticker": ticker,
            "Strategy": strategy,
            "Return%": result["percent_return"],
            "Winrate": result["winrate"],
            "Trades": result["total_trades"]
        })
    return pd.DataFrame(results)