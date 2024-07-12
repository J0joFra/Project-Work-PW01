# Toxicity Ingredients Report Processing

## Scopo del Progetto

Questo progetto è stato sviluppato per automatizzare il processo di raccolta, analisi e memorizzazione di dati relativi agli ingredienti dei rapporti CIR (Cosmetic Ingredient Review). Questo processo è suddiviso in tre fasi principali:
1. **Raccolta dei dati JSON** e salvataggio in un file CSV.
2. **Estrazione dei dettagli dei report dai link degli ingredienti** e aggiornamento del file CSV.
3. **Estrazione dei valori specifici dai PDF dei report** e aggiornamento finale del file CSV.

## Strumenti Utilizzati

- **Linguaggio di Programmazione:** Python
- **Librerie:** 
  - `requests` per effettuare le richieste HTTP.
  - `csv` per la manipolazione dei file CSV.
  - `BeautifulSoup` per il parsing HTML.
  - `pandas` per la manipolazione dei dati.
  - `tqdm` per la visualizzazione della progressione delle operazioni.
  - `PyPDF2` per l'estrazione di testo dai file PDF.
  - `io` e `re` per la gestione degli stream e l'uso di espressioni regolari.

## Descrizione dei File di Codice

1. **Raccolta Dati JSON e Creazione del File CSV**
2. **Estrazione dei Dettagli dai Link degli Ingredienti**
3. **Estrazione di Valori dai PDF dei Report**

## Come è Stato Svolto

1. **Raccolta Dati JSON e Creazione del File CSV**:
   - Vengono effettuate richieste POST agli URL specificati per ottenere i dati JSON relativi agli ingredienti.
   - I dati estratti vengono scritti in un file CSV con intestazioni appropriate.
   - I duplicati vengono rimossi dal file CSV.

2. **Estrazione dei Dettagli dai Link degli Ingredienti**:
   - Viene letto il file CSV creato nella fase precedente.
   - Per ogni link di ingrediente, vengono estratti i dettagli dei report utilizzando BeautifulSoup per il parsing HTML.
   - I dettagli estratti (link del report, stato, data/referenza) vengono aggiunti al file CSV.

3. **Estrazione di Valori dai PDF dei Report**:
   - Viene letto il file CSV aggiornato nella fase precedente.
   - Per ogni link di PDF presente, viene estratto il testo del PDF e cercati i valori di LD50 e NOAEL utilizzando espressioni regolari.
   - I valori estratti vengono aggiunti al file CSV.


Il codice sorgente utilizzato per questo progetto è disponibile su GitHub: - [Codice su GitHub]([https://github.com/J0joFra/Toxicity_Dataset_Maker])
