import yfinance as yf
import pandas as pd
from indicators import rsi, ema

def analyze(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)

        if df.empty or len(df) < 30:
            return None

        df["Close"] = df["Close"].astype(float)
        df["Volume"] = df["Volume"].astype(float)

        df["RSI"] = rsi(df["Close"])
        df["EMA20"] = ema(df["Close"], 20)
        df["EMA50"] = ema(df["Close"], 50)
        df["VOL_MA20"] = df["Volume"].rolling(20).mean()
        df["HIGH20"] = df["Close"].rolling(20).max()

        last = df.iloc[-1].to_dict()
        prev = df.iloc[-2].to_dict()

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

        level = (
            "🟢 GÜÇLÜ ALIM" if score >= 7 else
            "🟡 ORTA SİNYAL" if score >= 4 else
            "🔴 ZAYIF"
        )

        return {
            "symbol": symbol,
            "score": score,
            "level": level,
            "reasons": reasons,
            "rsi": round(last["RSI"], 1)
        }

    except Exception as e:
        print(f"Hata {symbol}: {e}")
        return None