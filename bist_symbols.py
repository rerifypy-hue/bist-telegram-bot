import requests
from bs4 import BeautifulSoup

URL = "https://stockanalysis.com/list/borsa-istanbul/"

def get_bist_symbols():
    r = requests.get(URL, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table")
    symbols = []

    for row in table.tbody.find_all("tr"):
        code = row.find_all("td")[1].text.strip()
        symbols.append(code + ".IS")

    return symbols