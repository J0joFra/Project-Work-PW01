import requests
from PyPDF2 import PdfReader
import io
import re
import pandas as pd
from tqdm import tqdm

def extract_text_from_pdf_url(pdf_url):
    try:
        # Richiesta GET all'URL del PDF
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        # Leggo il contenuto del PDF
        file_stream = io.BytesIO(response.content)
        pdf_reader = PdfReader(file_stream)
        
        # Estraggo il testo da tutte le pagine del PDF
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving PDF: {e}")
        return None
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return None

def extract_values(text):
    # Definisco i pattern regex per LD50 e NOAEL
    ld50_pattern = re.compile(r'LD50\s*>\s*(\d+(\.\d+)?\s*\w+/kg)', re.IGNORECASE)
    noael_pattern = re.compile(r'NOAEL\s*>\s*(\d+(\.\d+)?\s*\w+/kg)', re.IGNORECASE)

    # Trovo tutte le occorrenze dei pattern nel testo
    ld50_matches = ld50_pattern.findall(text)
    noael_matches = noael_pattern.findall(text)

    # Dizionari per conservare i valori per specie
    species_ld50 = {'rabbit': [], 'mouse': [], 'rat': []}
    species_noael = {'rabbit': [], 'mouse': [], 'rat': []}

    # Associo i valori trovati alle specie
    for match in ld50_matches:
        value = match[0].strip()
        # In base all'animale cercato e il valore ottenuto
        if re.search(r'\brabbit\b', text, re.IGNORECASE):
            species_ld50['rabbit'].append(value)        
        elif re.search(r'\bmouse\b', text, re.IGNORECASE):
            species_ld50['mouse'].append(value)
        elif re.search(r'\brat\b', text, re.IGNORECASE):
            species_ld50['rat'].append(value)

    for match in noael_matches:
        value = match[0].strip()
        if re.search(r'\brabbit\b', text, re.IGNORECASE):
            species_noael['rabbit'].append(value)
        elif re.search(r'\bmouse\b', text, re.IGNORECASE):
            species_noael['mouse'].append(value)
        elif re.search(r'\brat\b', text, re.IGNORECASE):
            species_noael['rat'].append(value)

    return species_ld50, species_noael

def get_lowest_value(values):
    if not values:
        return ""
    numeric_values = []
    for v in values:
        if 'mL/kg' in v:
            matches = re.findall(r'\d+(\.\d+)?', v)
            if matches and matches[0]:
                try:
                    numeric_values.append(float(matches[0]))
                except ValueError:
                    continue
    if numeric_values:
        return f"{min(numeric_values)} mL/kg"
    return values[0]

def main():
    csv_file = 'CIR_Ingredients_Report_Final.csv'
    df = pd.read_csv(csv_file)

    # Aggiungo le colonne necessarie se non esistono
    for col in ['LD50 Rabbit', 'LD50 Mouse', 'LD50 Rat', 'NOAEL Rabbit', 'NOAEL Mouse', 'NOAEL Rat']:
        if col not in df.columns:
            df[col] = ""

    # Riga di partenza -> da modificare ogni volta
    start_row = 5900

    for index, row in tqdm(df.iterrows(), total=len(df)):
        if index < start_row:
            continue

        pdf_url = row['Link del report']
        if pd.notna(pdf_url):
            pdf_text = extract_text_from_pdf_url(pdf_url)
            
            if pdf_text:
                ld50_values, noael_values = extract_values(pdf_text)
                
                df.at[index, 'LD50 Rat'] = get_lowest_value(ld50_values['rat'])
                df.at[index, 'LD50 Rabbit'] = get_lowest_value(ld50_values['rabbit'])
                df.at[index, 'LD50 Mouse'] = get_lowest_value(ld50_values['mouse'])

                df.at[index, 'NOAEL Rat'] = get_lowest_value(noael_values['rat'])                       
                df.at[index, 'NOAEL Rabbit'] = get_lowest_value(noael_values['rabbit'])            
                df.at[index, 'NOAEL Mouse'] = get_lowest_value(noael_values['mouse'])
            else:
                print(f"Failed to retrieve or parse PDF from URL: {pdf_url}")

        # Salvo il file CSV ogni 100 righe,
        # In caso di standby o problemi ho dei valori salvati
        if index > 0 and index % 100 == 0:
            df.to_csv(csv_file, index=False)
            print(f"CSV file saved at row {index}.")

    # Salvo il file CSV finale
    df.to_csv(csv_file, index=False)
    print("Extraction and update completed successfully.")

if __name__ == "__main__":
    main()
