import streamlit as st
import requests
from datetime import datetime, timedelta
import asyncio

# Polygon.io API-Schlüssel
api_key = "vKBX_cLJLjJNKUMIMF4EFW6HLKK9vo3o"

# Trigger und Zeitbereich von Benutzer festlegen lassen
st.title("NASDAQ Stock Volume Tracker")
percentage_threshold = st.slider("Set percentage increase threshold:", min_value=5, max_value=200, value=10, step=5)
time_range = st.selectbox("Select time range for volume change:", ["7 days", "15 days", "30 days", "90 days"])

# Zeiträume definieren
days_map = {"7 days": 7, "15 days": 15, "30 days": 30, "90 days": 90}
selected_days = days_map[time_range]

# Alle NASDAQ Symbole abrufen
def get_all_nasdaq_symbols():
    url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&exchange=XNAS&active=true&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        symbols = [ticker['ticker'] for ticker in data['results']]
        return symbols
    else:
        return []

# Funktion für Batch-Verarbeitung
def batch_process_symbols(symbol_list, batch_size=100):
    for i in range(0, len(symbol_list), batch_size):
        batch = symbol_list[i:i + batch_size]
        triggered_stocks = get_volume_data_batch(batch, selected_days)

        if len(triggered_stocks) > 0:
            st.write(f"Triggered Stocks in Batch {i//batch_size + 1}:")
            for stock, change in triggered_stocks:
                st.write(f"{stock}: {change:.2f}% volume change")
        else:
            st.write(f"No stocks triggered in Batch {i//batch_size + 1}.")

# Hintergrundprozess zum Abrufen von Volumendaten
async def fetch_all_stocks_background(symbols):
    await batch_process_symbols(symbols)

# App starten, wenn der Nutzer auf "Scan Stocks" klickt
if st.button("Scan Stocks"):
    nasdaq_symbols = get_all_nasdaq_symbols()
    if nasdaq_symbols:
        asyncio.run(fetch_all_stocks_background(nasdaq_symbols))
    else:
        st.error("Failed to retrieve Nasdaq symbols.")
