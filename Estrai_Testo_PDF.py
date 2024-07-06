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
            # Add current line and some context lines before and after
            context = lines[max(0, i-2):min(len(lines), i+3)]
            relevant_text.extend(context)
    
    text_lines = "\n".join(relevant_text)
    return text_lines

def extract_values(text):
    # Define regular expressions for NOAEL and LD50
    ld50_pattern = re.compile(r'LD50\s*>\s*(\d+\s*\w+/kg)', re.IGNORECASE)
    noael_pattern = re.compile(r'NOAEL\s*>\s*(\d+\s*\w+/kg)', re.IGNORECASE)

    # Find all matches in the text
    ld50_matches = ld50_pattern.findall(text)
    noael_matches = noael_pattern.findall(text)

    # Initialize species dictionaries
    species_ld50 = {'rabbit': [], 'mouse': [], 'rat': []}
    species_noael = {'rabbit': [], 'mouse': [], 'rat': []}

    # Check for matches and assign to appropriate species
    for match in ld50_matches:
        if re.search(r'\brabbit\b', text, re.IGNORECASE):
            species_ld50['rabbit'].append(match)
        elif re.search(r'\bmouse\b', text, re.IGNORECASE):
            species_ld50['mouse'].append(match)
        elif re.search(r'\brat\b', text, re.IGNORECASE):
            species_ld50['rat'].append(match)

    for match in noael_matches:
        if re.search(r'\brabbit\b', text, re.IGNORECASE):
            species_noael['rabbit'].append(match)
        elif re.search(r'\bmouse\b', text, re.IGNORECASE):
            species_noael['mouse'].append(match)
        elif re.search(r'\brat\b', text, re.IGNORECASE):
            species_noael['rat'].append(match)

    print(f"LD50 values: {species_ld50}")
    print(f"NOAEL values: {species_noael}")

# Extract text from PDF
pdf_url = "https://cir-reports.cir-safety.org/view-attachment/?id=94742a1a-c561-614f-9f89-14ce58abfc0b"
pdf_text = extract_text_from_pdf_url(pdf_url)

if pdf_text:
    keywords = ['LD50', 'NOAEL', 'rabbit', 'mouse', 'rat']
    relevant_text = extract_relevant_text(pdf_text, keywords)
    extract_values(relevant_text)
else:
    print("Failed to retrieve the PDF.")
