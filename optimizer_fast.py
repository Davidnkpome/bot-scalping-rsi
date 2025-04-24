# optimizer_fast.py
import random
import pandas as pd
from core_bot import run_backtest
from multiprocessing import Pool, cpu_count
import streamlit as st

def single_run(params):
    ticker, start_date, end_date, strategy, capital, ma_short, ma_long, tp, sl = params
    try:
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
        return {
            "MA_Short": ma_short,
            "MA_Long": ma_long,
            "TP": tp,
            "SL": sl,
            "Return%": result["percent_return"],
            "Winrate": result["winrate"],
            "Trades": result["total_trades"]
        }
    except Exception as e:
        return {"error": str(e)}

def optimize_strategy_fast(ticker, start_date, end_date, strategy="MA Crossover", capital=10000, n_iter=30):
    ma_short_values = [10, 15, 20, 25]
    ma_long_values = [30, 50, 100, 150]
    tp_values = [0.05, 0.1, 0.2]
    sl_values = [0.03, 0.05, 0.1]

    all_params = []
    while len(all_params) < n_iter:
        ma_s = random.choice(ma_short_values)
        ma_l = random.choice(ma_long_values)
        if ma_s >= ma_l:
            continue
        tp = random.choice(tp_values)
        sl = random.choice(sl_values)
        all_params.append((ticker, start_date, end_date, strategy, capital, ma_s, ma_l, tp, sl))

    results = []
    with Pool(cpu_count()) as pool:
        progress = st.progress(0)
        for i, res in enumerate(pool.imap(single_run, all_params)):
            if res and "error" not in res:
                results.append(res)
            progress.progress((i + 1) / len(all_params))

    df = pd.DataFrame(results)
    best = df.sort_values("Return%", ascending=False).iloc[0].to_dict() if not df.empty else {}

    if best:
        st.balloons()
        st.success(f"🚀 Config optimale trouvée : {best}")

    return best, df