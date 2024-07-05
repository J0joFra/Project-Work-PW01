import requests
from PyPDF2 import PdfReader
import io
import pandas as pd
import re

def extract_text_from_pdf_url(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        file_stream = io.BytesIO(response.content)
        pdf_reader = PdfReader(file_stream)
        
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        
        return text
    else:
        return None

def find_relevant_lines(text):
    lines = text.split('\n')
    relevant_lines = []
    keywords = ["noael", "dl50"]
    animals = ["rat", "mouse"]
    
    for line in lines:
        lower_line = line.lower()
        if any(keyword in lower_line for keyword in keywords) and any(animal in lower_line for animal in animals):
            relevant_lines.append(line)
    return relevant_lines

def extract_values(lines):
    noael_rat_values = []
    noael_mouse_values = []
    dl50_rat_values = []
    dl50_mouse_values = []
    
    for line in lines:
        line_lower = line.lower()
        if "noael" in line_lower:
            if "rat" in line_lower:
                values = re.findall(r'\d+\.?\d*', line)
                noael_rat_values.extend(map(float, values))
            if "mouse" in line_lower:
                values = re.findall(r'\d+\.?\d*', line)
                noael_mouse_values.extend(map(float, values))
        if "dl50" in line_lower:
            if "rat" in line_lower:
                values = re.findall(r'\d+\.?\d*', line)
                dl50_rat_values.extend(map(float, values))
            if "mouse" in line_lower:
                values = re.findall(r'\d+\.?\d*', line)
                dl50_mouse_values.extend(map(float, values))
    
    return {
        "noael_rat": min(noael_rat_values) if noael_rat_values else None,
        "noael_mouse": min(noael_mouse_values) if noael_mouse_values else None,
        "dl50_rat": min(dl50_rat_values) if dl50_rat_values else None,
        "dl50_mouse": min(dl50_mouse_values) if dl50_mouse_values else None
    }

# Esempio di utilizzo
pdf_url = "https://cir-reports.cir-safety.org/view-attachment/?id=94742a1a-c561-614f-9f89-14ce58abfc0b"
pdf_text = extract_text_from_pdf_url(pdf_url)
if pdf_text:
    relevant_lines = find_relevant_lines(pdf_text)
    values = extract_values(relevant_lines)
    
    data = {
        "NOAEL Rat": [values["noael_rat"]],
        "NOAEL Mouse": [values["noael_mouse"]],
        "DL50 Rat": [values["dl50_rat"]],
        "DL50 Mouse": [values["dl50_mouse"]]
    }
    
    df = pd.DataFrame(data)
    df.to_excel("toxicity_values.xlsx", index=False)
    print("File Excel creato con successo!")
else:
    print("Non è stato possibile estrarre il testo dal PDF.")
