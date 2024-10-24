import requests
import json

# Polygon.io API-Schlüssel (ersetze mit deinem eigenen Schlüssel)
api_key = "vKBX_cLJLjJNKUMIMF4EFW6HLKK9vo3o"

# URL für den Abruf der NASDAQ Symbole
base_url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&exchange=XNAS&active=true&apiKey={api_key}"

# Funktion zum Abrufen und Speichern aller NASDAQ Symbole mit Pagination
def download_and_save_all_symbols():
    symbols = []
    url = base_url
    while url:  # Schleife durch die Seiten der API-Ergebnisse
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            symbols.extend([ticker['ticker'] for ticker in results])
            
            # Überprüfen, ob es eine nächste Seite gibt
            next_url = data.get('next_url', None)
            if next_url:
                url = next_url + f"&apiKey={api_key}"  # Zur nächsten Seite wechseln
            else:
                url = None  # Keine weiteren Seiten
        else:
            print(f"Error fetching data: {response.status_code}")
            break
    
    # Symbole in einer JSON-Datei speichern
    with open('nasdaq_symbols.json', 'w') as f:
        json.dump(symbols, f)

    print(f"Downloaded {len(symbols)} NASDAQ symbols and saved to 'nasdaq_symbols.json'.")

# Abrufen und Speichern der NASDAQ Symbole
download_and_save_all_symbols()
