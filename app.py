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

    # Manuelle Erkennung bestimmter Schlüsselwörter
    if "kunde" in text.lower() or "kunden" in text.lower():
        if "bern" in entities:
            return f"ADR/adresse?$filter=contains(Ort,'Bern')&$top=3", ["AdressNr", "Name", "Vorname", "Strasse", "PLZ", "Ort"]
        else:
            return "ADR/adresse?$top=3", ["AdressNr", "Name", "Vorname", "Strasse", "PLZ", "Ort"]
    elif "umsatz" in text.lower() and ("hypobank" in text.lower() or "firma" in text.lower()):
        if "st. gallen" in text.lower():
            return f"VOL/umsatz?$filter=contains(Firma,'Hypobank St. Gallen')&$top=3", ["UmsatzNr", "Firma", "Betrag", "Datum"]
        else:
            return "VOL/umsatz?$top=3", ["UmsatzNr", "Firma", "Betrag", "Datum"]
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
    
    # Sicherstellen, dass jedes Element in der Liste ein flaches Dictionary ist
    filtered_data = []
    for item in data:
        flat_item = {}
        for field in fields:
            value = item.get(field, "")
            if isinstance(value, dict):
                # Wenn das Feld ein Dictionary ist, flachen wir es auf
                for subkey, subvalue in value.items():
                    flat_item[f"{field}_{subkey}"] = subvalue
            elif isinstance(value, list):
                # Wenn das Feld eine Liste ist, umwandeln wir sie in einen String
                flat_item[field] = ', '.join(map(str, value))
            else:
                flat_item[field] = value
        filtered_data.append(flat_item)

    # Logge die aufbereiteten Daten, um die Struktur zu überprüfen
    st.write("Aufbereitete Daten für DataFrame:", filtered_data)

    # Erstelle ein DataFrame für die Anzeige
    try:
        df = pd.DataFrame(filtered_data)
        st.dataframe(df)
    except ValueError as e:
        st.error(f"Fehler bei der Datenumwandlung: {e}")
        st.write(filtered_data)  # Zeige die problematischen Daten an

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
