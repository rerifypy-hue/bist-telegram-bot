import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
import os

TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

BIST = [
    "AKBNK.IS", "GARAN.IS", "YKBNK.IS",
    "ASELS.IS", "KRDMD.IS", "THYAO.IS"
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

signals = []

for symbol in BIST:
    df = yf.download(symbol, period="3mo", interval="1d", progress=False)
    if len(df) < 50:
        continue

    df["EMA20"] = ta.ema(df["Close"], length=20)
    df["EMA50"] = ta.ema(df["Close"], length=50)
    df["VOL_AVG"] = df["Volume"].rolling(20).mean()

    last = df.iloc[-1]

    if (
        last["EMA20"] > last["EMA50"] and
        last["Volume"] > last["VOL_AVG"] * 1.5
    ):
        signals.append(
            f"📈 {symbol}\n"
            f"Kapanış: {last['Close']:.2f}\n"
            f"Hacim Patlaması 🚀"
        )

if signals:
    send_telegram("🔔 BIST GÜNLÜK SİNYALLER\n\n" + "\n\n".join(signals))
else:
    send_telegram("❌ Bugün sinyal yok")
