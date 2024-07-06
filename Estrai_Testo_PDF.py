import requests
from PyPDF2 import PdfReader
import io
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

def extract_relevant_text(text, keywords):
    lines = text.split('\n')
    relevant_text = []
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in keywords):
            # Aggiungi la linea corrente e alcune righe di contesto prima e dopo
            context = lines[max(0, i-2):min(len(lines), i+3)]
            relevant_text.extend(context)
            
    text_lines= "\n".join(relevant_text)
    print(text_lines)

def extract_number(text):
    match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?)( [a-zA-Z/]+)', text)
    if match:
        number = match.group(1).replace(',', '.')
        unit = match.group(2).strip().lower()
        
        conversion_factors = {
            'mg/kg': 1,
            'g/kg': 1000,
            'µg/kg': 0.001,
            'microgram/kg': 0.001,
            'mcg/kg': 0.001,
            'mg/g': 1000
        }
        
        if unit in conversion_factors:
            return float(number) * conversion_factors[unit]
        else:
            return None
    return None

def extract_values(text):
    noael_rat = []
    noael_mouse = []
    ld50_rat = []
    ld50_mouse = []
    
    pattern_noael = re.compile(r'NOAEL\s*[:\-]?\s*(\d+(?:,\d+)?(?:\.\d+)?(?: [a-zA-Z/]+)?)', re.IGNORECASE)
    pattern_ld50 = re.compile(r'LD50\s*[:\-]?\s*(\d+(?:,\d+)?(?:\.\d+)?(?: [a-zA-Z/]+)?)', re.IGNORECASE)
    
    matches_noael = pattern_noael.findall(text)
    print(f"noael trovati: {matches_noael}")
    matches_ld50 = pattern_ld50.findall(text)
    print(f"ld50 trovati: {matches_ld50}")
    
    for match in matches_noael:
        value = extract_number(match)
        if value is not None:
            if 'rat' in text.lower():
                noael_rat.append(value)
            if 'mouse' in text.lower() or 'mice' in text.lower():
                noael_mouse.append(value)
    print(f"noael rat: {noael_rat}")
    print(f"noael mouse: {noael_mouse}")
    
    for match in matches_ld50:
        value = extract_number(match)
        if value is not None:
            if 'rat' in text.lower():
                ld50_rat.append(value)
            if 'mouse' in text.lower() or 'mice' in text.lower():
                ld50_mouse.append(value)
    print(ld50_mouse)
    print(ld50_rat) 
    
    min_noael_rat = min(noael_rat) if noael_rat else None
    min_noael_mouse = min(noael_mouse) if noael_mouse else None
    min_ld50_rat = min(ld50_rat) if ld50_rat else None
    min_ld50_mouse = min(ld50_mouse) if ld50_mouse else None
    
    return (min_noael_rat, min_noael_mouse), (min_ld50_rat, min_ld50_mouse)

# Estrai il testo dal PDF
pdf_url = "https://cir-reports.cir-safety.org/view-attachment/?id=94742a1a-c561-614f-9f89-14ce58abfc0b"
pdf_text = extract_text_from_pdf_url(pdf_url)

if pdf_text:
    keywords = ["NOAEL", "LD50"]
    relevant_text = extract_relevant_text(pdf_text, keywords)

    (noael_rat, noael_mouse), (ld50_rat, ld50_mouse) = extract_values(relevant_text)

    final_response = f"Il valore minimo di NOAEL per ratti è: {noael_rat} mg/kg.\n"
    final_response += f"Il valore minimo di NOAEL per topi è: {noael_mouse} mg/kg.\n"
    final_response += f"Il valore minimo di LD50 per ratti è: {ld50_rat} mg/kg.\n"
    final_response += f"Il valore minimo di LD50 per topi è: {ld50_mouse} mg/kg."
    print(final_response)
    
else:
    print("Non è stato possibile estrarre il testo dal PDF.") 
