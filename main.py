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
top = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

if not top:
    print("📉 Bugün BIST genelinde güçlü bir sinyal oluşmadı.")
    exit()

msg = []





for r in top:
    # Skoruna göre doluluk barı ve ikon belirleme
    if r["score"] >= 8:
        bar = "▰▰▰"  # Tam dolu
        status_icon = "🟢"
    elif r["score"] >= 6:
        bar = "▰▰▱"  # Orta dolu
        status_icon = "🟡"
    else:
        bar = "▰▱▱"  # Düşük dolu
        status_icon = "🔴"
    
    # RSI'yı tam sayı yap 
    rsi_val = int(r['rsi'])
    symbol = r['symbol'].replace(".IS", "").upper()
    # FORMAT: [SYSTEM_SCAN] altındaki satırlar
    msg.append(
        f"{bar} #{symbol:<5} ❯ RSI:{rsi_val:>2} ❯ S:{r['score']:02}"
    )

# Tweet'i birleştirme
header = "［ ＳＹＳＴＥＭ＿ＳＣＡＮ ］\n"
footer = "\n#BIST"
final = header + "\n" + "\n".join(msg) + footer



send("\n".join(final))
