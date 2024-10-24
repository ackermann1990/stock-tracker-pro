import streamlit as st
import requests
from datetime import datetime, timedelta

# Polygon.io API-Schlüssel
api_key = "vKBX_cLJLjJNKUMIMF4EFW6HLKK9vo3o"

# Trigger- und Filter-Einstellungen
st.title("NASDAQ Stock Volume Tracker")
percentage_threshold = st.slider("Set percentage increase threshold:", min_value=5, max_value=200, value=10, step=5)
time_range = st.selectbox("Select time range for volume change:", ["7 days", "15 days", "30 days", "90 days"])

# Zeiträume definieren
days_map = {"7 days": 7, "15 days": 15, "30 days": 30, "90 days": 90}
selected_days = days_map[time_range]

# Funktion zum Abrufen der NASDAQ Symbole (aus der API)
def get_all_nasdaq_symbols():
    url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&exchange=XNAS&active=true&apiKey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        symbols = [ticker['ticker'] for ticker in data['results']]
        return symbols
    else:
        return []

# Volumenänderungen für die Symbole abrufen
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

# Alle Symbole und Volumendaten verarbeiten
nasdaq_symbols = get_all_nasdaq_symbols()
triggered_stocks = []
neutral_stocks = []

# Prozess für das Abrufen der Volumendaten und Trigger-Check
for symbol in nasdaq_symbols:
    volumes = get_volume_data(symbol, selected_days)
    
    if len(volumes) > 0:
        current_volume = volumes[-1]
        avg_volume = sum(volumes[:-1]) / len(volumes[:-1])

        vol_change = ((current_volume - avg_volume) / avg_volume) * 100
        
        if vol_change >= percentage_threshold:
            triggered_stocks.append((symbol, vol_change))
        else:
            neutral_stocks.append(symbol)

# Anzeige der getriggerten Aktien
if triggered_stocks:
    st.subheader("Triggered Stocks")
    cols = st.columns(10)  # 10 Symbole pro Zeile
    for i, (symbol, change) in enumerate(triggered_stocks):
        cols[i % 10].write(f"**{symbol}**: {change:.2f}%")

# Anzeige der neutralen (grauen) Aktien
if neutral_stocks:
    st.subheader("Other Stocks")
    cols = st.columns(10)  # 10 Symbole pro Zeile
    for i, symbol in enumerate(neutral_stocks):
        cols[i % 10].write(f"{symbol}")
        cols[i % 10].markdown("<div style='color: gray;'>⬛</div>", unsafe_allow_html=True)
