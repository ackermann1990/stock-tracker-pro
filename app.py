import json

# Pfad zu deiner TXT-Datei
txt_file_path = 'nasdaq_symbols.txt'  # Ersetze das durch deinen Dateinamen
json_file_path = 'nasdaq_symbols.json'

# TXT-Datei lesen und in JSON umwandeln
def txt_to_json(txt_file_path, json_file_path):
    symbols_data = []
    
    # Öffne die TXT-Datei
    with open(txt_file_path, mode='r') as txt_file:
        # Überspringe die Kopfzeile (erste Zeile)
        next(txt_file)
        
        # Zeilenweise lesen
        for line in txt_file:
            # Entferne Leerzeichen und teile die Zeile an den Tabs (\t)
            symbol, description = line.strip().split('\t')
            
            # Füge die Daten als Dictionary in die Liste ein
            symbols_data.append({'symbol': symbol.strip(), 'description': description.strip()})
    
    # JSON-Datei schreiben
    with open(json_file_path, mode='w') as json_file:
        json.dump(symbols_data, json_file, indent=4)
    
    print(f"Successfully converted {len(symbols_data)} entries to JSON and saved to '{json_file_path}'")

# Konvertierung starten
txt_to_json(txt_file_path, json_file_path)
