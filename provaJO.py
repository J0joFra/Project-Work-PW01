import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import re

def fetch_noael_value(report_url):
    response = requests.get(report_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Supponiamo che il valore di Noael sia tra i contenuti del report
        report_content = soup.find(id='ContentContainer_ContentBottom_reportContent')
        if report_content:
            # Cerca tutte le occorrenze di Noael per topi e ratti
            noael_pattern = re.compile(r'Noael.*?topi.*?ratti.*?(\d+(\.\d+)?)', flags=re.IGNORECASE)
            matches = re.findall(noael_pattern, report_content.get_text())
            if matches:
                # Trova il valore di Noael più basso
                min_value = min(float(match[0]) for match in matches)
                return min_value
    return None

def main():
    filename = r"C:\Users\JoaquimFrancalanci\OneDrive - ITS Angelo Rizzoli\Desktop\Progetti\Project Work\CIR_Ingredients_Report.xlsx"
    df = pd.read_excel(filename)

    if 'published_report_link' not in df.columns:
        print("La colonna 'published_report_link' non esiste nel file Excel.")
        return

    with tqdm(total=len(df)) as pbar:
        noael_values = []

        for link in df['published_report_link']:
            # Ora che hai il link al report, cerca il valore di Noael
            noael_value = fetch_noael_value(link)
            pbar.update(1)
            noael_values.append(noael_value)

    df['noael_value'] = noael_values

    df.to_excel(filename, index=False, sheet_name='CIR Ingredients Report')
    
    print("File Excel aggiornato con successo!")

if __name__ == "__main__":
    main()
