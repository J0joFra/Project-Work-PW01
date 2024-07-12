import requests
import csv

#Rrichiesta POST all'URL fornito
def fetch_data(url):
    response = requests.post(url)
    if response.status_code == 200:
        data = response.json() # Recupero i dati in formato JSON
        return [
            (
                item.get('pcpc_ingredientid', ''), # Estraggo pcpc_ingredientid
                item.get('pcpc_ingredientname', ''), # Estraggo pcpc_ingredientname 
                f"https://cir-reports.cir-safety.org/cir-ingredient-status-report/?id={item.get('pcpc_ingredientid', '')}" # Costruisco un link utilizzando pcpc_ingredientid
            )
            for item in data.get('results', [])
        ]
    else:
        print(f"Errore nella richiesta: {response.status_code} - {response.reason}")
        return []

# Salvo i dati in un file CSV con il nome specificato
def save_to_csv(data, filename):
    headers = ['pcpc_ingredientid', 'pcpc_ingredientname', 'link']
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers) # Scrivo l'intestazione e ogni riga di dati.
        writer.writerows(data)
    print(f"File CSV creato con successo: {filename}")

def main():
    urls = [
        "https://cir-reports.cir-safety.org/FetchCIRReports/", #a-p
        "https://cir-reports.cir-safety.org/FetchCIRReports/?&pagingcookie=%26lt%3bcookie%20page%3d%26quot%3b1%26quot%3b%26gt%3b%26lt%3bpcpc_name%20last%3d%26quot%3bPEG-50%20Stearate%26quot%3b%20first%3d%26quot%3b1%2c10-Decanediol%26quot%3b%20%2f%26gt%3b%26lt%3bpcpc_ingredientidname%20last%3d%26quot%3bPEG-50%20Stearate%26quot%3b%20first%3d%26quot%3b1%2c10-Decanediol%26quot%3b%20%2f%26gt%3b%26lt%3bpcpc_cirrelatedingredientsid%20last%3d%26quot%3b%7bC223037E-F278-416D-A287-2007B9671D0C%7d%26quot%3b%20first%3d%26quot%3b%7b940AF697-52B5-4A3A-90A6-B9DB30EF4A7E%7d%26quot%3b%20%2f%26gt%3b%26lt%3b%2fcookie%26gt%3b&page=2"
    ]

    all_data = []
    for url in urls:
        data = fetch_data(url)
        all_data.extend(data)

    # Save data to CSV
    filename = 'CIR_Ingredients_Report.csv'
    save_to_csv(all_data, filename)

if __name__ == "__main__":
    main()
