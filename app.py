import streamlit as st
import requests
from datetime import datetime, timedelta
import json
import os

# Polygon.io API-Schlüssel
api_key = "vKBX_cLJLjJNKUMIMF4EFW6HLKK9vo3o"

# Funktion zum Abrufen der NASDAQ Symbole und einmaliges Speichern
def download_and_save_nasdaq_symbols():
    url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&exchange=XNAS&active=true&apiKey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        symbols = [ticker['ticker'] for ticker in data['results']]
        with open('nasdaq_symbols.json', 'w') as f:
            json.dump(symbols, f)
        return symbols
    else:
        return []

# Laden der Symbole aus der Datei, falls vorhanden
def load_nasdaq_symbols():
    if os.path.exists('nasdaq_symbols.json'):
        with open('nasdaq_symbols.json', 'r') as f:
            return json.load(f)
    else:
        return download_and_save_nasdaq_symbols()

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

# Funktion für die Pop-up-Anzeige (Modal) der Volumeninformationen
def show_popup(symbol, avg_volume):
    st.markdown(f"""
        <div style="background-color: lightgrey; padding: 20px; border-radius: 10px; margin: 10px;">
        <strong>{symbol}</strong><br>
        <p>3-month average volume: {avg_volume:.2f}</p>
        </div>
    """, unsafe_allow_html=True)

# Layout für abgerundete rechteckige Kacheln
def render_tile(symbol, color, avg_volume):
    if st.button(f"{symbol}"):
        show_popup(symbol, avg_volume)

    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:10px; text-align:center; margin:5px;">
        <span style="font-size:20px; color:white;">{symbol}</span>
        </div>
    """, unsafe_allow_html=True)

# Anwendung starten
nasdaq_symbols = load_nasdaq_symbols()

# Trigger- und Filter-Einstellungen
st.title("NASDAQ Stock Volume Tracker")
percentage_threshold = st.slider("Set percentage increase threshold:", min_value=5, max_value=200, value=10, step=5)
time_range = st.selectbox("Select time range for volume change:", ["7 days", "15 days", "30 days", "90 days"])

# Zeiträume definieren
days_map = {"7 days": 7, "15 days": 15, "30 days": 30, "90 days": 90}
selected_days = days_map[time_range]

# Placeholder für getriggerte und neutrale Symbole
triggered_stocks = []
neutral_stocks = []

# Durch alle Symbole iterieren und das Handelsvolumen überprüfen
for symbol in nasdaq_symbols:
    avg_volume = get_avg_volume(symbol, 3)
    if avg_volume:
        # In der Realität würdest du hier auch die Volumenveränderung basierend auf dem Trigger berechnen
        if avg_volume > 1000000:  # Beispiel-Trigger (volumenbasierter Vergleich)
            triggered_stocks.append((symbol, avg_volume))
        else:
            neutral_stocks.append((symbol, avg_volume))

# Anzeige der getriggerten Aktien oben in grünen Kacheln
if triggered_stocks:
    st.subheader("Triggered Stocks")
    cols = st.columns(10)  # 10 Symbole pro Zeile
    for i, (symbol, avg_volume) in enumerate(triggered_stocks):
        with cols[i % 10]:
            render_tile(symbol, "#28a745", avg_volume)

# Anzeige der neutralen (grauen) Aktien in Kacheln
if neutral_stocks:
    st.subheader("Other Stocks")
    cols = st.columns(10)  # 10 Symbole pro Zeile
    for i, (symbol, avg_volume) in enumerate(neutral_stocks):
        with cols[i % 10]:
            render_tile(symbol, "#6c757d", avg_volume)
