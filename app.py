import streamlit as st
import requests
import hashlib
import textrazor

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
client = textrazor.TextRazor(extractors=["entities", "topics", "phrases"])

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

# Funktion zur Analyse des Benutzereingabetextes mit TextRazor und Zuordnung zu API-Endpunkten
def analyze_and_map(text):
    response = client.analyze(text)
    entities = {entity.id.lower(): entity.matched_text for entity in response.entities()}
    st.write("Erkannte Entitäten:", entities)

    # Beispiel für Mapping von Entitäten zu API-Endpunkten
    if "kundennummer" in entities:
        kundennummer = entities["kundennummer"]
        return f"ADR/adresse?$filter=AdressNr eq {kundennummer}&$top=1", ["Name", "Strasse", "PLZ", "Ort"]
    elif "mailadresse" in entities and "firma" in entities:
        firma = entities["firma"]
        return f"ADR/adresse?$filter=contains(Name,'{firma}')&$top=1", ["EMail"]
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

# Funktion zur Darstellung der relevanten Daten
def display_data(data, fields):
    if not data:
        st.info("Keine Daten gefunden.")
        return

    filtered_data = []
    for item in data:
        flat_item = {}
        for field in fields:
            flat_item[field] = item.get(field, "")
        filtered_data.append(flat_item)
    
    st.write(filtered_data)

# Streamlit Interface
def main():
    st.title("Proffix Kundendaten Chatbot")

    # Chat-Eingabe
    user_input = st.text_input("Geben Sie Ihre Anfrage ein:", "")

    if st.button("Senden"):
        session_id = login_to_api()
        if session_id:
            endpoint, fields = analyze_and_map(user_input)
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
