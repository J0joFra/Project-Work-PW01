import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

def fetch_published_report_link(ingredient_url, pbar):
    response = requests.get(ingredient_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        sub_info_content = soup.find(id='ContentContainer_ContentBottom_subInfoContent')
        if sub_info_content:
            link_tag = sub_info_content.find('a', string='Published Report', href=True)
            if link_tag:
                attachment_link = f"https://cir-reports.cir-safety.org/{link_tag['href']}"
                pbar.update(1)  # Aggiorna la barra di avanzamento
                return attachment_link
    pbar.update(1)  # Aggiorna la barra anche se non c'è un link trovato
    return ""

def main():
    # Carica il file Excel esistente
    filename = r"C:\Users\JoaquimFrancalanci\OneDrive - ITS Angelo Rizzoli\Desktop\Progetti\Project Work\CIR_Ingredients_Report.xlsx"
    df = pd.read_excel(filename)

    # Assicurati che ci sia una colonna 'link' nel DataFrame
    if 'link' not in df.columns:
        print("La colonna 'link' non esiste nel file Excel.")
        return

    # Crea una barra di avanzamento tqdm
    with tqdm(total=len(df)) as pbar:
        attachment_links = []
        for link in df['link']:
            attachment_link = fetch_published_report_link(link, pbar)
            attachment_links.append(attachment_link)

    # Aggiungere la nuova colonna 'published_report_link' nel DataFrame
    df['published_report_link'] = attachment_links

    # Scrivere i dati aggiornati nel file Excel
    df.to_excel(filename, index=False, sheet_name='CIR Ingredients Report')
    
    print("File Excel aggiornato con successo!")

# Esegui la funzione principale
if __name__ == "__main__":
    main()
    
    