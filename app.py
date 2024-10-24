import streamlit as st
import requests
import json

# Polygon.io API-Schlüssel
api_key = "vKBX_cLJLjJNKUMIMF4EFW6HLKK9vo3o"

# URL für den Abruf der NASDAQ Symbole
base_url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&exchange=XNAS&active=true&apiKey={api_key}"

# Funktion zum Abrufen und Speichern aller NASDAQ Symbole mit Pagination
def download_and_save_all_symbols():
    symbols = []
    url = base_url
    progress = st.progress(0)  # Fortschrittsanzeige
    i = 0
    while url:  # Schleife durch die Seiten der API-Ergebnisse
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            symbols.extend([ticker['ticker'] for ticker in results])
            
            # Fortschrittsanzeige aktualisieren
            i += 1
            progress.progress(i / 10)  # Beispielhaft, setze hier einen geeigneten Wert für die Gesamtanzahl

            # Überprüfen, ob es eine nächste Seite gibt
            next_url = data.get('next_url', None)
            if next_url:
                url = next_url + f"&apiKey={api_key}"  # Zur nächsten Seite wechseln
            else:
                url = None  # Keine weiteren Seiten
        else:
            st.error(f"Error fetching data: {response.status_code}")
            break
    
    # Symbole in einer JSON-Datei speichern
    with open('nasdaq_symbols.json', 'w') as f:
        json.dump(symbols, f)

    st.success(f"Downloaded {len(symbols)} NASDAQ symbols and saved to 'nasdaq_symbols.json'.")

# Streamlit UI
st.title("Download NASDAQ Symbols")

if st.button("Download Symbols"):
    download_and_save_all_symbols()
else:
    st.write("Click the button to start downloading NASDAQ symbols.")
