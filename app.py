import streamlit as st
import requests
import hashlib
import textrazor

# TextRazor API-Schlüssel setzen
textrazor.api_key = "a416add172f24a9d5a2e4dda72139660b524d408c182af88aa4f7f08"

# TextRazor Client initialisieren
client = textrazor.TextRazor(extractors=["entities", "topics"])

# API URL und Login-Daten
API_URL = "https://portal.proffix.net:11011/pxapi/V4"
API_PASSWORD = "Demo_2016_PWREST!,Wangs"
DATABASE_NAME = "DEMODB"
USER = "Gast"
PASSWORD = "gast123"
MODULE = ["VOL"]

# Hash das Passwort für den Login
hashed_password = hashlib.sha256(PASSWORD.encode()).hexdigest()

# Login Daten im JSON Format
login_data = {
    "Benutzer": USER,
    "Passwort": hashed_password,
    "Datenbank": {"Name": DATABASE_NAME},
    "Module": MODULE
}

# Funktion zum Login in die API
def login_to_api():
    response = requests.post(f"{API_URL}/PRO/Login", json=login_data)
    if response.status_code == 200:
        return response.json().get("SessionId")
    else:
        st.error("Login failed!")
        return None

# Funktion zur Anfrage an die API
def request_data(session_id, endpoint):
    headers = {
        "SessionId": session_id
    }
    response = requests.get(f"{API_URL}/{endpoint}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Request failed!")
        return None

# Funktion zur Analyse des Benutzereingabetextes mit TextRazor
def analyze_text(text):
    response = client.analyze(text)
    keywords = [entity.id.lower() for entity in response.entities()]

    # Schlüsselwörter erkennen und entsprechende Endpunkte zuordnen
    if "kunden" in keywords or "adresse" in keywords:
        return "ADR/adresse?limit=3&depth=3"
    elif "artikel" in keywords:
        return "ART/artikel?limit=3&depth=3"
    elif "auftrag" in keywords:
        return "VOL/auftrag?limit=3&depth=3"
    else:
        return None

# Streamlit Interface
def main():
    st.title("Proffix Kundendaten Chatbot")

    # Chat-Eingabe
    user_input = st.text_input("Geben Sie Ihre Anfrage ein:", "")

    if st.button("Senden"):
        session_id = login_to_api()
        if session_id:
            endpoint = analyze_text(user_input)
            if endpoint:
                data = request_data(session_id, endpoint)
                if data:
                    st.json(data)
            else:
                st.info("Unbekannte Anfrage. Bitte versuchen Sie es erneut.")

if __name__ == "__main__":
    main()
