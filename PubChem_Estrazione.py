import requests
from PyPDF2 import PdfReader
import io
import re
import pandas as pd
from tqdm import tqdm

def extract_text_from_pdf_url(pdf_url):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        file_stream = io.BytesIO(response.content)
        pdf_reader = PdfReader(file_stream)
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
    ld50_pattern = re.compile(r'LD50\s*>\s*(\d+(\.\d+)?\s*\w+/kg)', re.IGNORECASE)
    noael_pattern = re.compile(r'NOAEL\s*>\s*(\d+(\.\d+)?\s*\w+/kg)', re.IGNORECASE)
    ld50_matches = ld50_pattern.findall(text)
    noael_matches = noael_pattern.findall(text)
    species_ld50 = {'rabbit': [], 'mouse': [], 'rat': []}
    species_noael = {'rabbit': [], 'mouse': [], 'rat': []}
    for match in ld50_matches:
        value = match[0].strip()
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

def get_pubchem_data(ingredient_name):
    url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/annotations/heading/JSON/?source=Hazardous%20Substances%20Data%20Bank%20(HSDB)&heading_type=Compound&heading=Non-Human%20Toxicity%20Values%20(Complete)&page=1'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=header)
    response = response.json()
    ingredients_list = response["Annotations"]["Annotation"]
    for ingredient in ingredients_list:
        if ingredient["Name"].lower() == ingredient_name.lower():
            data = ingredient["Data"]
            values = [el["Value"]["StringWithMarkup"][0]["String"] for el in data if "Value" in el]
            sources = [el["Reference"][0] for el in data if "Reference" in el]
            return values, sources
    return [], []

def main():
    excel_file = r"C:\Users\JoaquimFrancalanci\OneDrive - ITS Angelo Rizzoli\Desktop\Progetti\Project Work\CIR_Ingredients_Report_Final.xlsx"
    df = pd.read_excel(excel_file)
    
    print("Colonne disponibili nel DataFrame:")
    print(df.columns)

    for col in ['LD50 Rabbit', 'LD50 Mouse', 'LD50 Rat', 'NOAEL Rabbit', 'NOAEL Mouse', 'NOAEL Rat']:
        if col not in df.columns:
            df[col] = ""
    
    start_row = 0
    for index, row in tqdm(df.iterrows(), total=len(df)):
        if index < start_row:
            continue
        
        if all(pd.isna(row[col]) for col in ['LD50 Rabbit', 'LD50 Mouse', 'LD50 Rat', 'NOAEL Rabbit', 'NOAEL Mouse', 'NOAEL Rat']):
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
            else:
                ingredient_name = row['pcpc_ingredientname']
                pubchem_values, pubchem_sources = get_pubchem_data(ingredient_name)
                if pubchem_values:
                    ld50_rabbit = [val for val in pubchem_values if 'rabbit' in val.lower() and 'ld50' in val.lower()]
                    ld50_mouse = [val for val in pubchem_values if 'mouse' in val.lower() and 'ld50' in val.lower()]
                    ld50_rat = [val for val in pubchem_values if 'rat' in val.lower() and 'ld50' in val.lower()]
                    noael_rabbit = [val for val in pubchem_values if 'rabbit' in val.lower() and 'noael' in val.lower()]
                    noael_mouse = [val for val in pubchem_values if 'mouse' in val.lower() and 'noael' in val.lower()]
                    noael_rat = [val for val in pubchem_values if 'rat' in val.lower() and 'noael' in val.lower()]
                    df.at[index, 'LD50 Rat'] = get_lowest_value(ld50_rat)
                    df.at[index, 'LD50 Rabbit'] = get_lowest_value(ld50_rabbit)
                    df.at[index, 'LD50 Mouse'] = get_lowest_value(ld50_mouse)
                    df.at[index, 'NOAEL Rat'] = get_lowest_value(noael_rat)
                    df.at[index, 'NOAEL Rabbit'] = get_lowest_value(noael_rabbit)
                    df.at[index, 'NOAEL Mouse'] = get_lowest_value(noael_mouse)
        else:
            print(f"Skipping ingredient at row {index} as it already has values.")
        
        if index > 0 and index % 100 == 0:
            df.to_excel(excel_file, index=False)
            print(f"Excel file saved at row {index}.")
    
    df.to_excel(excel_file, index=False)
    print("Extraction and update completed successfully.")

if __name__ == "__main__":
    main()
