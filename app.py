import streamlit as st
import requests
import hashlib
import textrazor
import pandas as pd

# TextRazor API-Schlüssel setzen
textrazor.api_key = "a416add172f24a9d5a2e4dda72139660b524d408c182af88aa4f7f08"

# API URL und Login-Daten
API_URL = "https://portal.proffix.net:11011/pxapi/V4"
DATABASE_NAME = "DEMODB"
USER = "Gast"
PASSWORD = "gast123"
MODULE = ["VOL"]

# Erzeuge den SHA-256 Hash des Passworts
hashed_password = hashlib.sha256(PASSWORD.encode()).hexdigest()

# Login Daten im JSON Format
login_data = {
    "Benutzer": USER,
    "Passwort": hashed_password,
    "Datenbank": {"Name": DATABASE_NAME},
    "Module": MODULE
}

# TextRazor Client initialisieren
client = textrazor.TextRazor(extractors=["entities", "topics"])

# Funktion zum Login in die API
def login_to_api():
    response = requests.post(f"{API_URL}/PRO/Login", json=login_data)
    
    if response.status_code == 200 or response.status_code == 201:
        session_id = response.headers.get("PxSessionId")
        if session_id:
            return session_id
        else:
            st.error("Session ID not found in response headers.")
            return None
    else:
        st.error(f"Login failed! Status code: {response.status_code}, Response: {response.text}")
        return None

# Funktion zur Analyse des Benutzereingabetextes mit TextRazor
def analyze_text(text):
    response = client.analyze(text)
    entities = {entity.id.lower(): entity.matched_text for entity in response.entities()}
    
    st.write("Erkannte Entitäten:", entities)

    # Erkennung von Entitäten und Ableitung der API-Anfrage
    if "kunde" in entities:
        if "ort" in entities:
            ort = entities["ort"]
            return f"ADR/adresse?filter=Ort eq '{ort}'&depth=3", ["AdressNr", "Name", "Vorname", "Strasse", "PLZ", "Ort"]
        else:
            return "ADR/adresse?limit=3&depth=3", ["AdressNr", "Name", "Vorname", "Strasse", "PLZ", "Ort"]
    elif "umsatz" in entities and "firma" in entities:
        firma = entities["firma"]
        return f"VOL/umsatz?filter=Firma eq '{firma}'&depth=3", ["UmsatzNr", "Firma", "Betrag", "Datum"]
    else:
        return None, []

# Funktion zur Anfrage an die API
def request_data(session_id, endpoint):
    headers = {
        "PxSessionId": session_id
    }
    response = requests.get(f"{API_URL}/{endpoint}", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Request failed! Status code: {response.status_code}, Response: {response.text}")
        return None

# Funktion zur Filterung und Darstellung der relevanten Daten
def display_data(data, fields):
    if not data:
        st.info("Keine Daten gefunden.")
        return
    
    # Extrahiere nur die relevanten Felder aus den Daten
    filtered_data = [{field: item.get(field, "") for field in fields} for item in data]
    
    # Erstelle ein DataFrame für die Anzeige
    df = pd.DataFrame(filtered_data)
    
    # Zeige das DataFrame in einer sauberen Tabelle an
    st.dataframe(df)

# Streamlit Interface
def main():
    st.title("Proffix Kundendaten Chatbot")

    # Chat-Eingabe
    user_input = st.text_input("Geben Sie Ihre Anfrage ein:", "")

    if st.button("Senden"):
        session_id = login_to_api()
        if session_id:
            endpoint, fields = analyze_text(user_input)
            if endpoint:
                data = request_data(session_id, endpoint)
                if data:
                    display_data(data, fields)
            else:
                st.info("Unbekannte Anfrage. Bitte versuchen Sie es erneut.")
        else:
            st.error("Login failed! Please check your credentials and try again.")

if __name__ == "__main__":
    main()
