import requests
from bs4 import BeautifulSoup

URL = "https://stockanalysis.com/list/borsa-istanbul/"

def get_bist_symbols():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")

    symbols = []

    for row in table.tbody.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:
            symbol = cols[1].text.strip()
            symbols.append(symbol + ".IS")  # yfinance formatı

    return sorted(symbols)

if __name__ == "__main__":
    bist_symbols = get_bist_symbols()

    print(f"Toplam hisse sayısı: {len(bist_symbols)}")
    print(bist_symbols)
