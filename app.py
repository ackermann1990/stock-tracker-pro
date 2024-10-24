import streamlit as st
import requests
from datetime import datetime, timedelta

# Polygon.io API-Schlüssel
api_key = "vKBX_cLJLjJNKUMIMF4EFW6HLKK9vo3o"

# Nutzeroptionen für Trigger
st.title("NASDAQ Stock Volume Tracker")
percentage_threshold = st.slider("Set percentage increase threshold:", min_value=5, max_value=200, value=10, step=5)
time_range = st.selectbox("Select time range for volume change:", ["7 days", "15 days", "30 days", "90 days"])

# Zeiträume definieren
days_map = {"7 days": 7, "15 days": 15, "30 days": 30, "90 days": 90}
selected_days = days_map[time_range]

# Funktion zum Abrufen der NASDAQ Aktien (dummy Funktion für symbol list)
def get_nasdaq_symbols():
    # In der Realität würde hier eine Liste der NASDAQ Symbole abgerufen werden.
    # Für das Beispiel nur einige Symbole
    return ["AAPL", "MSFT", "GOOGL"]

# Funktion zum Abrufen der Volumendaten
def get_volume_data(symbol, days):
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}?apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        volumes = [day['v'] for day in data['results']]
        return volumes
    else:
        return []

# Hintergrundabruf für alle NASDAQ Aktien
if st.button("Check Stocks"):
    st.write(f"Checking for stocks with volume changes over {percentage_threshold}% in the last {time_range}...")

    nasdaq_symbols = get_nasdaq_symbols()
    triggered_stocks = []

    for symbol in nasdaq_symbols:
        volumes = get_volume_data(symbol, selected_days)
        
        if len(volumes) > 0:
            current_volume = volumes[-1]
            avg_volume = sum(volumes[:-1]) / len(volumes[:-1])
            
            # Volumenänderung berechnen
            vol_change = ((current_volume - avg_volume) / avg_volume) * 100
            
            if vol_change >= percentage_threshold:
                triggered_stocks.append((symbol, vol_change))
    
    # Ergebnisse anzeigen
    if len(triggered_stocks) > 0:
        st.write(f"Stocks triggered with volume change over {percentage_threshold}%:")
        for stock, change in triggered_stocks:
            st.write(f"{stock}: {change:.2f}% volume change")
    else:
        st.write("No stocks triggered.")

