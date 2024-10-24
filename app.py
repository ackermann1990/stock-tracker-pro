import streamlit as st

# Datei-Upload über Streamlit
uploaded_file = st.file_uploader("Choose a TXT file with NASDAQ symbols", type="txt")

# Wenn eine Datei hochgeladen wird, konvertiere sie in Python-Code
if uploaded_file is not None:
    # Speichere die hochgeladene Datei vorübergehend
    symbols_data = []
    
    # TXT-Datei einlesen und in Python-Code umwandeln
    for line in uploaded_file:
        # Konvertiere die Byte-Zeilen zu String
        line = line.decode('utf-8').strip()
        
        # Überspringe leere Zeilen oder die Kopfzeile
        if not line or 'Symbol' in line:
            continue
        
        # Teile die Zeile bei einem Tabulatorzeichen (\t) auf
        symbol, description = line.split('\t', 1)
        
        # Füge das Symbol und die Beschreibung zur Liste hinzu
        symbols_data.append({"symbol": symbol.strip(), "description": description.strip()})
    
    # Python-Code generieren (ohne f-string)
    python_code = "nasdaq_symbols = [\n"
    for entry in symbols_data:
        python_code += "    {'symbol': '" + entry['symbol'] + "', 'description': '" + entry['description'] + "'},\n"
    python_code += "]"
    
    # Zeige den generierten Python-Code in einem Textfeld an
    st.code(python_code, language='python')

    # Biete den Download des generierten Codes als Python-Datei an
    st.download_button(
        label="Download Python Code",
        data=python_code,
        file_name='nasdaq_symbols.py',
        mime='text/x-python'
    )
