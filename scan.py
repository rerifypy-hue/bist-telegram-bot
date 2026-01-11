import yfinance as yf
import pandas as pd
import ta
import requests
import os

TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

# Tüm BIST hisseleri (önceden yazdığımız scriptten geliyor varsayımı)
from get_bist_symbols import get_bist_symbols
BIST = get_bist_symbols()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    })

# --- ENDEKS FİLTRESİ (XU100) ---
xu100 = yf.download("XU100.IS", period="2mo", interval="1d", progress=False)
if isinstance(xu100.columns, pd.MultiIndex):
    xu100.columns = xu100.columns.get_level_values(0)

xu100["EMA20"] = ta.trend.ema_indicator(xu100["Close"], window=20)
xu100_trend_ok = xu100.iloc[-1]["Close"] > xu100.iloc[-1]["EMA20"]

if not xu100_trend_ok:
    send_telegram("⚠️ *XU100 negatif – bugün sinyal üretilmedi*")
    exit()

signals = []

for symbol in BIST:
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)

        if df.empty or len(df) < 50:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        volume = df["Volume"]

        df["EMA20"] = ta.trend.ema_indicator(close, window=20)
        df["EMA50"] = ta.trend.ema_indicator(close, window=50)
        df["RSI"] = ta.momentum.rsi(close, window=14)
        df["VOL_AVG"] = volume.rolling(20).mean()

        # Bollinger
        bb = ta.volatility.BollingerBands(close)
        df["BB_UP"] = bb.bollinger_hband()
        df["BB_LOW"] = bb.bollinger_lband()
        df["BB_WIDTH"] = df["BB_UP"] - df["BB_LOW"]

        last = df.iloc[-1]
        prev = df.iloc[-2]

        # --- SİNYAL 1: TREND + HACİM ---
        if (
            last["EMA20"] > last["EMA50"] and
            last["RSI"] > 50 and
            last["Volume"] > last["VOL_AVG"] * 1.5
        ):
            signals.append(f"📈 *{symbol}* → Trend + Hacim")

        # --- SİNYAL 2: BREAKOUT ---
        resistance = high[-20:].max()
        if (
            last["Close"] > resistance and
            last["Volume"] > last["VOL_AVG"] * 1.5
        ):
            signals.append(f"🚀 *{symbol}* → Direnç Kırılımı")

        # --- SİNYAL 3: RSI DİPTEN DÖNÜŞ ---
        if prev["RSI"] < 30 and last["RSI"] > 30 and last["Close"] > prev["Close"]:
            signals.append(f"🔄 *{symbol}* → RSI Dipten Dönüş")

        # --- SİNYAL 4: BOLLINGER SIKIŞMA ---
        if (
            df["BB_WIDTH"][-10:].mean() < df["BB_WIDTH"][-30:].mean() * 0.7 and
            last["Close"] > last["BB_UP"]
        ):
            signals.append(f"⚡ *{symbol}* → Bollinger Kırılımı")

    except Exception as e:
        print(f"Hata {symbol}: {e}")

if signals:
    send_telegram("🔔 *BIST GÜNLÜK SİNYALLER*\n\n" + "\n".join(signals))
else:
    send_telegram("❌ *Bugün kriterlere uyan sinyal yok*")