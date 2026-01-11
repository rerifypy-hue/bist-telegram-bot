import yfinance as yf
import pandas as pd
import ta
import requests
import os

# Telegram bilgileri (GitHub Secrets)
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

# İzlenecek BIST hisseleri (isteğe göre artır)
BIST = [
    "AKBNK.IS",
    "GARAN.IS",
    "YKBNK.IS",
    "ASELS.IS",
    "THYAO.IS",
    "KRDMD.IS",
    "PETKM.IS",
    "SISE.IS"
]

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
            progress=False
        )

        if df.empty or len(df) < 50:
            continue

        # Teknik indikatörler
        df["EMA20"] = ta.trend.ema_indicator(df["Close"], window=20)
        df["EMA50"] = ta.trend.ema_indicator(df["Close"], window=50)
        df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
        df["VOL_AVG"] = df["Volume"].rolling(20).mean()

        last = df.iloc[-1]

        # Sinyal şartları
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

# Telegram mesajı
if signals:
    message = "🔔 *BIST GÜNLÜK SİNYALLER*\n\n" + "\n\n".join(signals)
else:
    message = "❌ *Bugün sinyal yok*"

send_telegram(message)
