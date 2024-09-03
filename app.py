import streamlit as st
import requests

# Streamlit-App-Titel
st.title("Kundendaten Chatbot")

# API-Zugriffsdaten
api_url = "https://portal.proffix.net:11011/api"
headers = {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
    'Content-Type': 'application/json'
}

# Benutzer-Eingabe
query = st.text_input("Fragen Sie nach Kundendaten:")

# Abfragefunktion
def query_customer_data(query):
    response = requests.get(f"{api_url}/customers", headers=headers)
    if response.status_code == 200:
        customers = response.json()
        # Hier könntest du eine intelligente Interpretation des Abfrage-Texts einbauen.
        # Zum Beispiel kannst du hier eine einfache Suche in den Kundendaten durchführen:
        for customer in customers:
            if query.lower() in customer['name'].lower():
                return customer
        return {"info": "Kein Kunde gefunden"}
    else:
        return {"error": "Fehler beim Abrufen der Daten"}

# Wenn die Abfrage eingegeben wurde, Daten anzeigen
if query:
    result = query_customer_data(query)
    st.json(result)

