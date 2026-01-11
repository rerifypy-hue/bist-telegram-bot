import yfinance as yf
import pandas as pd
from indicators import rsi, ema

def analyze(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if df.empty or len(df) < 30:
            return None

        close = df["Close"].squeeze()
        volume = df["Volume"].squeeze()

        df["RSI"] = rsi(close)
        df["EMA20"] = ema(close, 20)
        df["EMA50"] = ema(close, 50)
        df["VOL_MA20"] = volume.rolling(20).mean()
        df["HIGH20"] = close.rolling(20).max()

        last = df.iloc[-1]
        prev = df.iloc[-2]

        score = 0
        reasons = []

        if prev["RSI"] < 30 and last["RSI"] > 30:
            score += 2; reasons.append("RSI 30 üstü")

        if last["RSI"] > 50:
            score += 1; reasons.append("RSI > 50")

        if last["EMA20"] > last["EMA50"]:
            score += 2; reasons.append("EMA20 > EMA50")

        if last["Close"] > last["EMA20"]:
            score += 1; reasons.append("Fiyat EMA20 üstü")

        if last["Volume"] > last["VOL_MA20"]:
            score += 2; reasons.append("Hacim artışı")

        if last["Close"] >= last["HIGH20"]:
            score += 2; reasons.append("20g direnç kırılımı")

        if score >= 7:
            level = "🟢 GÜÇLÜ ALIM"
        elif score >= 4:
            level = "🟡 ORTA SİNYAL"
        else:
            level = "🔴 ZAYIF"

        return {
            "symbol": symbol,
            "score": score,
            "level": level,
            "reasons": reasons,
            "rsi": round(last["RSI"], 1)
        }

    except Exception as e:
        print(e)
        return None