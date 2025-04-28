import requests
import pandas as pd
import time
from tqdm import tqdm


def load_distilleries_info():
    """
    Carica le informazioni di base su tutte le distillerie dall'API WhiskyHunter.
    
    Returns:
        pandas.DataFrame: DataFrame con informazioni sulle distillerie
    """
    url = "https://whiskyhunter.net/api/distilleries_info/"
    
    try:
        # Facciamo una richiesta GET all'API e salviamo in JSON
        response = requests.get(url)
        response.raise_for_status()  # Verifica se ci sono stati errori
        d_info = response.json()
        d_info = pd.DataFrame(d_info)
        
        # Convertiamo in integer o float gestendo eventuali errori
        d_info["whiskybase_rating"] = pd.to_numeric(d_info["whiskybase_rating"], errors="coerce")
        d_info["whiskybase_whiskies"] = pd.to_numeric(d_info["whiskybase_whiskies"], errors="coerce")
        d_info["whiskybase_votes"] = pd.to_numeric(d_info["whiskybase_votes"], errors="coerce")
        
        return d_info
    except requests.exceptions.RequestException as e:
        print(f"Errore durante il caricamento dei dati: {e}")
        return pd.DataFrame()

def load_distillery_data(slug):
    """
    Carica i dati storici di mercato per una specifica distilleria.
    
    Args:
        slug (str): L'identificativo della distilleria
        
    Returns:
        pandas.DataFrame: DataFrame con i dati storici della distilleria
    """
    url = f"https://whiskyhunter.net/api/distillery_data/{slug}/"
    
    try:
        # Facciamo una richiesta GET all'API e salviamo in JSON
        response = requests.get(url)
        response.raise_for_status()  # Verifica se ci sono stati errori
        data = response.json()
        
        # Se non ci sono dati, ritorniamo un DataFrame vuoto
        if not data:
            return pd.DataFrame()
        
        # Convertiamo i dati in un DataFrame
        df = pd.DataFrame(data)
        
        # Convertiamo la data in formato datetime e gli altri valori in float
        df['dt'] = pd.to_datetime(df['dt'])
        numeric_columns = ['winning_bid_max', 'winning_bid_min', 'winning_bid_mean', 'trading_volume', 'lots_count']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        return df
    except requests.exceptions.RequestException as e:
        print(f"Errore durante il caricamento dei dati per {slug}: {e}")
        return pd.DataFrame()

def build_combined_dataframe(top_n=50, wait_time=0.1):
    """
    Costruisce il DataFrame combinato per l'analisi di dashboard.
    
    Args:
        top_n (int): Il numero di distillerie con rating più alto da analizzare
        wait_time (float): Tempo di attesa tra le richieste API per evitare sovraccarichi
        
    Returns:
       df_data è il DataFrame con i dati storici di tutte le distillerie
    """
    # Carica le informazioni di base sulle distillerie
    df_info = load_distilleries_info()
    if df_info.empty:
        return df_info, pd.DataFrame()
    
    # Filtra per le distillerie con rating più alto
    top_distilleries = df_info.sort_values(by="whiskybase_rating", ascending=False).head(top_n)
    
    # Prepara una lista per i dati storici
    all_data = []
    
    # Per ogni distilleria nella lista, carica i dati storici
    print(f"Caricamento dati per le {top_n} distillerie con rating più alto...")
    for _, row in tqdm(top_distilleries.iterrows(), total=len(top_distilleries), desc="Caricamento dati distillerie"):
        slug = row['slug']
        distillery_data = load_distillery_data(slug)
        
        if not distillery_data.empty:
            all_data.append(distillery_data)
        
        # Breve pausa per non sovraccaricare l'API
        time.sleep(wait_time)
    
    # Se non sono stati caricati dati, ritorna un DataFrame vuoto
    if not all_data:
        return df_info, pd.DataFrame()
    
    # Combina tutti i dati storici in un unico DataFrame
    df_data = pd.concat(all_data, ignore_index=True)
    
    return df_data
'''
if __name__ == "__main__":
    # Test delle funzioni
    df_info, df_data = build_combined_dataframe(top_n=5)  # Test con solo 5 distillerie
    
    print(f"Informazioni distillerie: {df_info.shape[0]} righe, {df_info.shape[1]} colonne")
    if not df_info.empty:
        print(df_info.head())
    
    print(f"Dati storici: {df_data.shape[0]} righe, {df_data.shape[1]} colonne")
    if not df_data.empty:
        print(df_data.head())
'''