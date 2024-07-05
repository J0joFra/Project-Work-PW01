import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

def fetch_report_details(ingredient_url, pbar):
    response = requests.get(ingredient_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'ContentContainer_ContentBottom_ingredientReferences'})
        
        if table:
            rows = table.find_all('tr')[1:]  # Ignora l'intestazione
            reports = []
            
            for row in rows:
                cells = row.find_all('td')
                status_cell = cells[1]
                link_tag = status_cell.find('a')
                date_reference = cells[2].text.strip()
                
                if link_tag and 'report' in link_tag.text.lower():
                    report_link = f"https://cir-reports.cir-safety.org/{link_tag['href']}"
                    status = link_tag.text.strip()
                    reports.append((date_reference, report_link, status))
            
            if reports:
                # Prova a convertire la data, se fallisce lascia la stringa originale
                for report in reports:
                    try:
                        report_date = pd.to_datetime(report[0], format='%B %d, %Y')
                    except ValueError:
                        try:
                            report_date = pd.to_datetime(report[0], format='%Y')
                        except ValueError:
                            report_date = report[0]  # Mantieni il formato originale se non riconosciuto

                    report = (report_date, report[1], report[2])
                
                # Ordina i report per data in ordine decrescente e restituisci il più recente
                reports.sort(key=lambda x: x[0], reverse=True)
                pbar.update(1)
                return reports[0][1], reports[0][2], reports[0][0]
    
    pbar.update(1)
    return "null", "null", "null"

def main():
    # Carica il file Excel esistente
    filename = r"C:\Users\JoaquimFrancalanci\OneDrive - ITS Angelo Rizzoli\Desktop\Progetti\Project Work\CIR_Ingredients_Report.xlsx"
    df = pd.read_excel(filename)

    # Assicurati che ci sia una colonna 'link' nel DataFrame
    if 'link' not in df.columns:
        print("La colonna 'link' non esiste nel file Excel.")
        return

    # Crea una barra di avanzamento tqdm
    with tqdm(total=min(10, len(df))) as pbar:  # Limita la barra di avanzamento a 10 elementi o meno
        report_links = []
        statuses = []
        date_references = []
        
        # Itera solo sui primi 10 link
        for link in df['link'][:10]:
            report_link, status, date_reference = fetch_report_details(link, pbar)
            report_links.append(report_link)
            statuses.append(status)
            date_references.append(date_reference)

    # Aggiungere le nuove colonne nel DataFrame
    df.loc[:9, 'Link del report'] = report_links  # Solo per le prime 10 righe
    df.loc[:9, 'Stato'] = statuses
    df.loc[:9, 'Data/Referenza'] = date_references

    # Scrivere i dati aggiornati nel file Excel
    df.to_excel(filename, index=False, sheet_name='CIR Ingredients Report')
    
    print("File Excel aggiornato con successo!")

# Esegui la funzione principale
if __name__ == "__main__":
    main()
