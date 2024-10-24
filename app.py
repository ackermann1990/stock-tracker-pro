import requests
import json
from bs4 import BeautifulSoup

# URL für die NASDAQ Tickersymbole
url = 'https://www.nasdaq.com/market-activity/stocks/screener'

# Funktion zum Scrapen der NASDAQ Tickersymbole
def scrape_nasdaq_symbols():
    symbols = []
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extrahiere die Tickersymbole (dieses Beispiel hängt von der Struktur der Seite ab)
        table = soup.find('table', {'class': 'market-activity__stocks-screener-table'})
        if table:
            rows = table.find_all('tr')[1:]  # Überspringe die Kopfzeile
            for row in rows:
                symbol = row.find_all('td')[0].text.strip()
                symbols.append(symbol)

        # Speichere die Tickersymbole in einer JSON-Datei
        with open('nasdaq_symbols.json', 'w') as f:
            json.dump(symbols, f)
        print(f"Successfully scraped and saved {len(symbols)} symbols to 'nasdaq_symbols.json'.")
    else:
        print(f"Failed to retrieve data: {response.status_code}")

# Scrape NASDAQ Tickersymbole
scrape_nasdaq_symbols()
