import streamlit as st
import requests

# Polygon.io API Key
API_KEY = "vKBX_cLJLjJNKUMIMF4EFW6HLKK9vo3o"

# Importiere die Tickersymbole direkt aus der Datei nasdaq_tickers.py
from nasdaq_tickers import nasdaq_symbols

# Streamlit setup
st.title("Nasdaq Ticker Tracker")

# Funktion zum Abrufen des Handelsvolumens und Preises
def get_ticker_data(symbol):
    # Beispielhaftes Datum (dies kann später dynamisch gemacht werden)
    url = f"https://api.polygon.io/v1/open-close/{symbol}/2023-10-20?apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Anzeige der Tickersymbole in abgerundeten Kacheln
st.subheader("Ticker List")

# Hier zeigen wir die Tickersymbole und Beschreibungen an
for ticker in nasdaq_symbols:
    symbol = ticker['symbol']
    description = ticker['description']
    
    # API Call to get price and volume data
    data = get_ticker_data(symbol)
    
    if data and 'status' in data and data['status'] == 'OK':
        volume = data['volume']
        close_price = data['close']
        st.write(f"{symbol} - {description}: Volume: {volume}, Price: {close_price}")
    else:
        st.write(f"{symbol} - {description}: No data available or error retrieving data.")
