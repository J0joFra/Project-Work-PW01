import requests
from PyPDF2 import PdfReader
import io

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

# Esempio di utilizzo
pdf_url = "https://cir-reports.cir-safety.org/view-attachment/?id=94742a1a-c561-614f-9f89-14ce58abfc0b"
pdf_text = extract_text_from_pdf_url(pdf_url)
if pdf_text:
    print(pdf_text)
else:
    print("Non è stato possibile estrarre il testo dal PDF.")
