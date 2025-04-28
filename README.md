# Whisky Dashboard

Dashboard interattiva per l'analisi dei dati sulle distillerie di whisky, basata sui dati forniti da WhiskyHunter API.

## 🥃 Obiettivo del Progetto

Questa applicazione web interattiva sviluppata con Streamlit visualizza:
- Informazioni e classifiche sulle distillerie
- Analisi di mercato basate sui dati di vendita
- Confronti dinamici tra distillerie
- Prezzi e volumi di trading in sterline britanniche (£ GBP)

## 🗂️ Struttura del Progetto

```
whisky_dashboard/
├── data_loader.py       # Script per caricare e pre-processare tutti i dati
├── app.py               # Script principale Streamlit (UI)
├── requirements.txt     # Dipendenze
└── README.md            # Documentazione progetto con istruzioni
```

## 🧰 Tecnologie Usate

- Python 3.9+
- pandas per manipolazione dei dati
- requests per interazione con API
- Streamlit per l'interfaccia web interattiva
- Plotly per visualizzazioni avanzate e interattive

## 📊 Funzionalità Dashboard

La dashboard include diverse sezioni accessibili dal menu di navigazione:

1. **Panoramica**: Visualizza la distribuzione delle distillerie per paese e permette di esplorare le statistiche del dataset principale.

2. **Classifiche**: Visualizza le top 10 distillerie organizzate in tre categorie: rating, prezzo medio e volume di trading totale.

3. **Analisi Distilleria**: Permette di selezionare una singola distilleria (tra quelle con dati disponibili) per visualizzarne informazioni dettagliate.

4. **Confronto Distillerie**: Consente di selezionare e confrontare più distillerie simultaneamente, visualizzando grafici comparativi.

## 📥 Installazione

1. Clonare il repository o scaricare i file

2. Installare le dipendenze:
```
pip install -r requirements.txt
```

3. Avviare l'applicazione:
```
streamlit run app.py
```

## 🚀 Uso dell'Applicazione

1. Quando l'app si avvia, attendere il caricamento dei dati.
2. Utilizzare la sidebar a sinistra per navigare tra le diverse sezioni della dashboard.
3. Nella sezione "Classifiche", utilizzare le schede per visualizzare i diversi tipi di ranking.
4. Nella sezione "Analisi Distilleria", selezionare una distilleria dal menu a tendina per visualizzarne i dettagli.
   - Vengono mostrate solo le distillerie per cui sono disponibili dati.
5. Nella sezione "Confronto Distillerie", selezionare più distillerie dal selettore multiplo per confrontarle.
   - Vengono mostrate solo le distillerie per cui sono disponibili dati.

## 📄 Note sui Dati

- I dati provengono da WhiskyHunter API (https://whiskyhunter.net/api/).
- L'app carica i dati per le 50 distillerie con il rating più alto per ottimizzare i tempi di caricamento.
- Le analisi includono metadati statici (nome, paese, rating) e dati dinamici (prezzi, volumi).
- Tutti i valori monetari (prezzi di offerta e volumi di trading) sono espressi in sterline britanniche (£ GBP).
- Non tutte le distillerie hanno dati disponibili; l'interfaccia mostra solo quelle con dati effettivamente recuperati.

## 👩‍💻 Autrice
Erica Cutuli, PhD - Whisky Dashboard Project

*Progetto sviluppato all'interno del Coding Bootcamp AI Engineer di Edgemony*
