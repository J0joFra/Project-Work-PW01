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

def find_relevant_lines(text, keywords):
    lines = text.split('\n')
    relevant_lines = []
    for line in lines:
        if any(keyword in line.lower() for keyword in keywords):
            relevant_lines.append(line)
    return relevant_lines

def extract_values_from_lines(lines):
    noael_rat = float('inf')
    noael_mouse = float('inf')
    dl50_rat = float('inf')
    dl50_mouse = float('inf')

    for line in lines:
        if 'noael' in line.lower():
            if 'rat' in line.lower():
                noael_rat = min(noael_rat, extract_value(line))
            if 'mouse' in line.lower():
                noael_mouse = min(noael_mouse, extract_value(line))
        if 'dl50' in line.lower() or 'ld50' in line.lower():
            if 'rat' in line.lower():
                dl50_rat = min(dl50_rat, extract_value(line))
            if 'mouse' in line.lower():
                dl50_mouse = min(dl50_mouse, extract_value(line))
    
    # Replace float('inf') with None if no value was found
    noael_rat = None if noael_rat == float('inf') else noael_rat
    noael_mouse = None if noael_mouse == float('inf') else noael_mouse
    dl50_rat = None if dl50_rat == float('inf') else dl50_rat
    dl50_mouse = None if dl50_mouse == float('inf') else dl50_mouse

    return noael_rat, noael_mouse, dl50_rat, dl50_mouse

def extract_value(line):
    match = re.search(r'(\d+(\.\d+)?)', line)
    if match:
        return float(match.group(1))
    return float('inf')

# Example usage
pdf_url = "https://cir-reports.cir-safety.org/view-attachment/?id=94742a1a-c561-614f-9f89-14ce58abfc0b"
pdf_text = extract_text_from_pdf_url(pdf_url)
if pdf_text:
    keywords = ["noael", "dl50", "ld50", "rat", "mouse"]
    relevant_lines = find_relevant_lines(pdf_text, keywords)
    noael_rat, noael_mouse, dl50_rat, dl50_mouse = extract_values_from_lines(relevant_lines)
    print(f"NOAEL Rat: {noael_rat}")
    print(f"NOAEL Mouse: {noael_mouse}")
    print(f"DL50 Rat: {dl50_rat}")
    print(f"DL50 Mouse: {dl50_mouse}")
else:
    print("Non è stato possibile estrarre il testo dal PDF.")
