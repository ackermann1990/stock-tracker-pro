import streamlit as st
import json

# Datei-Upload über Streamlit
uploaded_file = st.file_uploader("Choose a TXT file with NASDAQ symbols", type="txt")

# Wenn eine Datei hochgeladen wird, konvertiere sie in JSON
if uploaded_file is not None:
    # Speichere die hochgeladene Datei vorübergehend
    symbols_data = []
    
    # TXT-Datei einlesen und in JSON umwandeln
    for line in uploaded_file:
        # Konvertiere die Byte-Zeilen zu String
        line = line.decode('utf-8')
        if "Symbol" in line:  # Kopfzeile überspringen
            continue
        # Entferne Leerzeichen und teile die Zeile an den Tabs (\t)
        symbol, description = line.strip().split('\t')
        # Füge die Daten als Dictionary in die Liste ein
        symbols_data.append({'symbol': symbol.strip(), 'description': description.strip()})
    
    # JSON-Datei anzeigen
    st.write(symbols_data)
    
    # Biete den Download der JSON-Datei an
    json_data = json.dumps(symbols_data, indent=4)
    st.download_button(
        label="Download JSON",
        data=json_data,
        file_name='nasdaq_symbols.json',
        mime='application/json'
    )
