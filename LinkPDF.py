import requests
from bs4 import BeautifulSoup

# URL della pagina web
url = "https://cir-reports.cir-safety.org/cir-ingredient-status-report/?id=b7c19dab-0272-44ae-a1e7-165991cb0be6"

# Effettua la richiesta HTTP alla pagina web
response = requests.get(url)

# Controlla se la richiesta è stata eseguita con successo
if response.status_code == 200:
    # Parsing del contenuto HTML della pagina web
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Trova la tabella specifica per ID
    table = soup.find('table', {'id': 'ContentContainer_ContentBottom_ingredientReferences'})
    
    if table:
        # Trova tutte le righe della tabella
        rows = table.find_all('tr')
        
        # La prima riga contiene l'intestazione, quindi la ignoreremo
        for row in rows[1:]:
            cells = row.find_all('td')
            ingredient = cells[0].text
            status_link = cells[1].find('a')['href']
            status = cells[1].text
            date_reference = cells[2].text
            
            # Stampa le informazioni estratte
            print(f"Ingrediente: {ingredient}")
            print(f"Link del report: {status_link}")
            print(f"Stato: {status}")
            print(f"Data/Referenza: {date_reference}")
            print("\n")
    else:
        print("Tabella non trovata nella pagina web.")
else:
    print(f"Errore durante la richiesta HTTP: {response.status_code}")
