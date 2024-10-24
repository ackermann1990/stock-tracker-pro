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

# Funktion zum Abrufen des durchschnittlichen Handelsvolumens
def get_avg_volume(symbol, months=3):
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=months*30)).strftime("%Y-%m-%d")

    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}?apiKey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        volumes = [day['v'] for day in data['results']]
        if volumes:
            return sum(volumes) / len(volumes)
    return None

# Layout für Kacheln
def render_tile(symbol, color, key):
    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:15px; text-align:center; cursor: pointer;" 
        onclick="window.location.href='#{key}'">
        <span style="font-size:20px; color:white;">{symbol}</span>
        </div>
    """, unsafe_allow_html=True)

# Getriggerte und neutrale Aktien filtern
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

# Abrufen aller Symbole und Verarbeiten der Volumendaten
nasdaq_symbols = get_all_nasdaq_symbols()
triggered_stocks = []
neutral_stocks = []

for symbol in nasdaq_symbols:
    volumes = get_volume_data(symbol, selected_days)
    
    if len(volumes) > 0:
        current_volume = volumes[-1]
        avg_volume = sum(volumes[:-1]) / len(volumes[:-1])

        vol_change = ((current_volume - avg_volume) / avg_volume) * 100
        
        if vol_change >= percentage_threshold:
            triggered_stocks.append(symbol)
        else:
            neutral_stocks.append(symbol)

# Anzeige der getriggerten Aktien oben in grünen Kacheln
if triggered_stocks:
    st.subheader("Triggered Stocks")
    cols = st.columns(10)  # 10 Symbole pro Zeile
    for i, symbol in enumerate(triggered_stocks):
        key = f"triggered_{i}"
        with cols[i % 10]:
            render_tile(symbol, "#28a745", key)

# Anzeige der neutralen (grauen) Aktien in Kacheln
if neutral_stocks:
    st.subheader("Other Stocks")
    cols = st.columns(10)  # 10 Symbole pro Zeile
    for i, symbol in enumerate(neutral_stocks):
        key = f"neutral_{i}"
        with cols[i % 10]:
            render_tile(symbol, "#6c757d", key)

# Klickbare Kacheln für Durchschnittsvolumen der letzten 3 Monate
for i, symbol in enumerate(nasdaq_symbols):
    if st.button(f"Show 3-month average volume for {symbol}"):
        avg_vol = get_avg_volume(symbol)
        if avg_vol:
            st.write(f"The 3-month average volume for {symbol} is {avg_vol}")
        else:
            st.write(f"No data available for {symbol}")
