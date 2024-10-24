import streamlit as st
import requests
import json
import os

# Polygon.io API-Schlüssel
api_key = "vKBX_cLJLjJNKUMIMF4EFW6HLKK9vo3o"

# Funktion zum Abrufen der NASDAQ Symbole und Speichern in einer JSON-Datei
def download_and_save_nasdaq_symbols():
    url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&exchange=XNAS&active=true&apiKey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        symbols = [ticker['ticker'] for ticker in data['results']]
        
        # Speichern der Symbole in einer JSON-Datei
        with open('nasdaq_symbols.json', 'w') as f:
            json.dump(symbols, f)
        
        return symbols
    else:
        st.error(f"Failed to retrieve symbols: {response.status_code}")
        return None

# Streamlit App UI
st.title("Download NASDAQ Symbols as JSON")

if st.button("Download Symbols"):
    symbols = download_and_save_nasdaq_symbols()
    if symbols:
        st.success(f"Successfully downloaded {len(symbols)} symbols.")
        
        # Biete den Download der JSON-Datei an
        with open("nasdaq_symbols.json", "r") as file:
            btn = st.download_button(
                label="Download NASDAQ Symbols JSON",
                data=file,
                file_name="nasdaq_symbols.json",
                mime="application/json"
            )
    else:
        st.error("Could not download symbols. Please check your API key or try again later.")
