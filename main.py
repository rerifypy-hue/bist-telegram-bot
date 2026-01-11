from bist_symbols import get_bist_symbols
from signal_engine import analyze
from telegram import send

symbols = get_bist_symbols()

results = []

for sym in symbols:
    result = analyze(sym)
    if not result:
        continue
    results.append(result)

# 🔝 En yüksek puanlılar
top = sorted(results, key=lambda x: x["score"], reverse=True)[:10]

if not top:
    send("📉 Bugün BIST genelinde güçlü bir sinyal oluşmadı.")
    exit()

msg = []
msg.append("📊 BIST GÜNLÜK SİNYAL TABLOSU\n")
msg.append("HİSSE     RSI   PUAN  SİNYAL")
msg.append("--------------------------------")

for r in top:
    level_icon = "🟢" if r["score"] >= 7 else "🟡"
    msg.append(
        f"#{r['symbol'][:6]:<8} "
        f"{r['rsi']:<5} "
        f"{r['score']:<4}  "
        f"{level_icon}"
    )

msg.append(f"\n📈 Toplam taranan hisse: {len(results)}")
send("\n".join(msg))