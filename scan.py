import yfinance as yf
import pandas as pd
import ta
import requests
import os
from get_bist_symbols import get_bist_symbols

TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

BIST = get_bist_symbols()

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

signals = []

for symbol in BIST:
    try:
        df = yf.download(
            symbol,
            period="3mo",
            interval="1d",
            progress=False,
            group_by="column"  # önemli
        )

        if df.empty or len(df) < 50:
            continue

        # 🔴 MULTIINDEX FIX (ASIL ÇÖZÜM)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Teknik indikatörler
        close = df["Close"]
        volume = df["Volume"]

        df["EMA20"] = ta.trend.ema_indicator(close, window=20)
        df["EMA50"] = ta.trend.ema_indicator(close, window=50)
        df["RSI"] = ta.momentum.rsi(close, window=14)
        df["VOL_AVG"] = volume.rolling(20).mean()

        last = df.iloc[-1]

        if (
            last["EMA20"] > last["EMA50"] and
            last["RSI"] > 50 and
            last["Volume"] > last["VOL_AVG"] * 1.5
        ):
            signals.append(
                f"📈 *{symbol}*\n"
                f"Kapanış: `{last['Close']:.2f}`\n"
                f"RSI: `{last['RSI']:.1f}`\n"
                f"Hacim Patlaması 🚀"
            )

    except Exception as e:
        print(f"Hata: {symbol} → {e}")

if signals:
    message = "🔔 *BIST GÜNLÜK SİNYALLER*\n\n" + "\n\n".join(signals)
else:
    message = "❌ *Bugün sinyal yok*"

send_telegram(message)
