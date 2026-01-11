from bist_symbols import get_bist_symbols
from signal_engine import analyze
from telegram import send

symbols = get_bist_symbols()

for sym in symbols:
    result = analyze(sym)
    if not result:
        continue

    print(sym, result["score"])

    if result["score"] >= 7:
        message = f"""
📊 {result['symbol']}
RSI: {result['rsi']}
Puan: {result['score']}/10
{result['level']}

Nedenler:
- """ + "\n- ".join(result["reasons"])

        send(message.strip())