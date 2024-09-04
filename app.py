import openai
import streamlit as st
import requests
import hashlib

# OpenAI GPT API-Schlüssel setzen
openai.api_key = "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"

# Proffix API URL und Login-Daten
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

# Funktion zum Login in die API
def login_to_api():
    response = requests.post(f"{API_URL}/PRO/Login", json=login_data)
    if response.status_code == 200 or response.status_code == 201:
        session_id = response.headers.get("PxSessionId")
        return session_id
    else:
        st.error("Login failed!")
        return None

# Funktion zur Interpretation der Anfrage durch ChatGPT
def interpret_query_with_chatgpt(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that maps user queries to Proffix ERP API calls."},
            {"role": "user", "content": f"Interpretiere die folgende Anfrage und mappe sie auf die relevanten Entitäten und API-Endpunkte im Proffix-ERP: {user_input}"}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

# Funktion zur dynamischen Erstellung der API-Anfrage basierend auf der Interpretation
def generate_api_request(interpreted_query):
    if "Kundennummer" in interpreted_query:
        kundennummer = interpreted_query.split("Kundennummer ")[1].split(" ")[0]
        return f"ADR/adresse?$filter=AdressNr eq {kundennummer}&$top=1", ["Name", "Strasse", "PLZ", "Ort"]
    elif "Mailadresse" in interpreted_query and "Firma" in interpreted_query:
        firma = interpreted_query.split("Firma ")[1].split(" ")[0]
        return f"ADR/adresse?$filter=contains(Name,'{firma}')&$top=1", ["EMail"]
    elif "Kunden aus" in interpreted_query and "Ort" in interpreted_query:
        ort = interpreted_query.split("Ort ")[1].split(" ")[0]
        return f"ADR/adresse?$filter=contains(Ort,'{ort}')", ["Name", "Strasse", "PLZ", "Ort"]
    else:
        return None, []

# Funktion zur Anfrage an die Proffix API
def request_data(session_id, endpoint):
    headers = {
        "PxSessionId": session_id
    }
    response = requests.get(f"{API_URL}/{endpoint}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Request failed!")
        return None

# Funktion zur Darstellung der Daten
def display_data(data, fields):
    if not data:
        st.info("Keine Daten gefunden.")
        return
    flat_data = [{field: item.get(field, "") for field in fields} for item in data]
    st.table(flat_data)

# Hauptfunktion für die WebApp
def main():
    st.title("Proffix ERP Intelligenter Chatbot")
    
    user_input = st.text_input("Geben Sie Ihre Anfrage ein:", "")
    
    if st.button("Senden"):
        session_id = login_to_api()
        if session_id:
            interpreted_query = interpret_query_with_chatgpt(user_input)
            st.write("Interpretierte Anfrage:", interpreted_query)
            endpoint, fields = generate_api_request(interpreted_query)
            if endpoint:
                data = request_data(session_id, endpoint)
                if data:
                    display_data(data, fields)
            else:
                st.error("Konnte die Anfrage nicht interpretieren.")
        else:
            st.error("Login fehlgeschlagen!")

if __name__ == "__main__":
    main()
