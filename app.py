import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data_loader import build_combined_dataframe, load_distilleries_info

# Configurazione della pagina
st.set_page_config(
    page_title="Whisky Dashboard",
    page_icon="🥃",
    layout="wide"
)

# Stile CSS personalizzato
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E3D59;
        }
        .sub-header {
            font-size: 1.8rem;
            color: #F5B971;
        }
        .stat-box {
            background-color: #F5F5F5;
            padding: 1rem;
            border-radius: 5px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Funzione per generare un gradiente di colori
def color_gradient(start_color, end_color, n):
    import matplotlib.colors as mcolors
    return [mcolors.to_hex(c) for c in mcolors.LinearSegmentedColormap.from_list("", [start_color, end_color])(np.linspace(0, 1, n))]
        

# Funzione per caricare i dati
@st.cache_data
def load_data(top_n=50):
    with st.spinner(f"Caricamento dei dati in corso..."):
        df_info = load_distilleries_info()
        if df_info.empty:
            st.error("Impossibile caricare i dati delle distillerie. Verifica la connessione e riprova.")
            return pd.DataFrame(), pd.DataFrame()
        df_data = build_combined_dataframe(top_n=top_n)
    return df_info, df_data
    

# Funzione per visualizzare la pagina principale con overview
def show_overview(df_info, df_data):
    st.title("🥃 Panoramica del Mercato del Whisky")
    # Layout a colonne per le metriche principali
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
        num_distilleries = len(df_info) if not df_info.empty else 0
        st.metric("Distillerie", num_distilleries)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
        if not df_info.empty and "whiskybase_rating" in df_info.columns:
            avg_rating = df_info["whiskybase_rating"].astype(float).mean()
            st.metric("Rating Medio", f"{avg_rating:.2f}/100")
        else:
            st.metric("Rating Medio", "N/A")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
        if not df_info.empty and "whiskybase_votes" in df_info.columns:
            avg_votes = df_info["whiskybase_votes"].astype(int).mean()
            st.metric("Numero medio di voti", f"{avg_votes:.0f}")
        else:
            st.metric("Numero medio di voti", "N/A")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Distribuzione per paese
    st.subheader("🌍 Distribuzione Distillerie per Paese")
    country_counts = df_info["country"].value_counts().reset_index()
    country_counts.columns = ["country", "count"]

    fig = px.pie(
        country_counts, 
        values="count", 
        names="country", 
        hole=0.4
    )

    fig.update_layout(
    showlegend=False
    )

    fig.update_traces(
        textfont_size=16,
        textposition='outside',
        textinfo='percent+label',
        pull=[0.05]*len(country_counts)
    )

    st.plotly_chart(fig)
        
    # Rating vs Numero di Whisky
    st.subheader("📌 Statistiche e Boxplot")
    # Per colonne numeriche, mostra statistiche
    numeric_cols = df_info.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if numeric_cols:
        stats_col = st.selectbox("Seleziona una colonna per l'analisi:", options=numeric_cols)
        stats = df_info[stats_col].describe()
        
        # Visualizza le statistiche in una tabella formattata
        st.subheader(f"Statistiche di {stats_col}")
        stats_df = pd.DataFrame(stats).transpose()
        st.dataframe(stats_df, use_container_width=True)
        
        # Crea un box plot
        fig = px.box(df_info, y=stats_col, 
                title=f"Box Plot di {stats_col}",
                color_discrete_sequence=['#3CB44B'])
        st.plotly_chart(fig, use_container_width=True)

# Funzione per visualizzare l'analisi di una singola distilleria
def show_distillery_analysis(df_info, df_data):
    st.title("📈 Analisi Distillerie")
    st.warning(f"⚠️ I dati di dettaglio sono disponibili solo per {len(df_data['slug'].unique())} distillerie tra quelle con rating più alto.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
        if not df_data.empty and "winning_bid_mean" in df_data.columns:
            avg_price = df_data["winning_bid_mean"].mean()
            st.metric("Prezzo Medio", f"GBP (£) {avg_price:.2f}")
        else:
            st.metric("Prezzo Medio", "N/A")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
        if not df_data.empty and "trading_volume" in df_data.columns:
            avg_vol = df_data['trading_volume'].mean()
            st.metric("Trading Volume Medio", f"GBP (£) {avg_vol:.2f}")
        else:
            st.metric("Prezzo Medio Aste", "N/A")
        st.markdown("</div>", unsafe_allow_html=True)
   
    st.markdown("---")
    
    # Ottieni solo le distillerie per cui abbiamo estratto i dati
    available_slugs = df_data['slug'].unique()
    available_distilleries = df_info[df_info['slug'].isin(available_slugs)].sort_values(by='name')
    
    # Selezione distilleria
    selected_distillery = st.selectbox(
        "Seleziona una distilleria:",
        options=available_distilleries['name'].tolist(),
        index=0
    )
    
    # Ottieni lo slug della distilleria selezionata
    slug = available_distilleries[available_distilleries['name'] == selected_distillery]['slug'].iloc[0]
    
    # Filtra i dati per la distilleria selezionata
    distillery_data = df_data[df_data['slug'] == slug]
    
    if distillery_data.empty:
        st.warning(f"Non ci sono dati disponibili per {selected_distillery}.")
        return
    
    # Informazioni sulla distilleria
    info = df_info[df_info['slug'] == slug].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Paese", info['country'])
    with col2:
        st.metric("Rating", f"{info['whiskybase_rating']:.2f}")
    with col3:
        st.metric("Numero di Whisky", int(info['whiskybase_whiskies']))
    
    # Trend prezzo medio
    fig = px.line(
        distillery_data,
        x='dt',
        y='winning_bid_mean',
        markers=True,
        labels={
            'dt': 'Data',
            'winning_bid_mean': 'Prezzo Medio (£ GBP)'},
            title=f"📈 Trend Prezzo Medio di {selected_distillery}")

    # Miglioramenti estetici
    fig.update_layout(
        title={'x': 0.1, 'font': {'size': 26}},
        xaxis_title='Data',
        yaxis_title='Prezzo Medio (£ GBP)',
        template='plotly_white',  # stile bianco pulito
        xaxis_tickangle=45,
        margin=dict(l=40, r=40, t=80, b=40),
        hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    # Volume di trading
    fig = px.bar(
    distillery_data,
    x='dt',
    y='trading_volume',
    labels={
        'dt': 'Data',
        'trading_volume': 'Volume (£ GBP)'},
        title=f"📊 Volume di Trading di {selected_distillery}")

    # Miglioramenti estetici
    fig.update_layout(
        title={'x': 0.1, 'font': {'size': 26}},
        xaxis_title='Data',
        yaxis_title='Volume (£ GBP)',
        template='plotly_white',  # stile bianco pulito
        xaxis_tickangle=45,
        margin=dict(l=40, r=40, t=80, b=40),
        hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# Funzione per visualizzare il confronto tra distillerie
def show_distillery_comparison(df_info, df_data):
    st.title("🔄 Confronto tra Distillerie")
    st.warning(f"⚠️ I dati di dettaglio sono disponibili solo per {len(df_data['slug'].unique())} distillerie tra quelle con rating più alto.")
    
    # Ottieni solo le distillerie per cui abbiamo estratto i dati
    available_slugs = df_data['slug'].unique()
    available_distilleries = df_info[df_info['slug'].isin(available_slugs)].sort_values(by='name')
    
    # Selezione multiple di distillerie
    all_distilleries = available_distilleries['name'].tolist()
    default_selections = all_distilleries[:3] if len(all_distilleries) >= 3 else all_distilleries
    selected_distilleries = st.multiselect(
        "Seleziona le distillerie da confrontare:",
        options=all_distilleries,
        default=default_selections
    )
    
    if not selected_distilleries:
        st.warning("Seleziona almeno una distilleria per visualizzare il confronto.")
        return
      # Ottieni gli slug delle distillerie selezionate
    selected_slugs = available_distilleries[available_distilleries['name'].isin(selected_distilleries)]['slug'].tolist()
    
    # Prepara i dati per il grafico
    compare_data = []
    for slug in selected_slugs:
        name = df_info[df_info['slug'] == slug]['name'].iloc[0]
        distillery_data = df_data[df_data['slug'] == slug]
        if not distillery_data.empty:
            compare_data.append((name, distillery_data))

    if not compare_data:
        st.warning("Non ci sono dati disponibili per le distillerie selezionate.")
        return

    # Crea il grafico con Plotly
    fig = go.Figure()

    for name, data in compare_data:
        fig.add_trace(
            go.Scatter(
                x=data['dt'], 
                y=data['winning_bid_mean'], 
                mode='lines+markers',
                name=name
            )
        )

    fig.update_layout(
        title={'text': "📈 Trend Prezzo Medio", 'x': 0.1, 'font': {'size': 26}},
        xaxis_title='Data',
        yaxis_title='Prezzo Medio (£ GBP)',
        template='plotly_white',
        xaxis_tickangle=45,
        margin=dict(l=40, r=40, t=80, b=40),
        hovermode="x unified",
        legend_title_text="Distilleria",
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Visualizzazione boxplot
    # Colori coerenti con plotly (puoi anche personalizzarli)
    color_sequence = px.colors.qualitative.Plotly

    # Crea il boxplot
    fig = go.Figure()

    for idx, (name, data) in enumerate(compare_data):
        fig.add_trace(
            go.Box(
                y=data['winning_bid_mean'],
                name=name,
                marker_color=color_sequence[idx % len(color_sequence)],
                boxmean=True,  # Mostra anche la media
                boxpoints='outliers'  # Mostra solo gli outlier
            )
        )

    fig.update_layout(
        title={'text': "📊 Boxplot Prezzo Medio", 'x': 0.1, 'font': {'size': 26}},
        yaxis_title='Prezzo Medio (£ GBP)',
        xaxis_title='Distilleria',
        template='plotly_white',
        margin=dict(l=40, r=40, t=80, b=50),
        boxmode='group'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Crea il grafico con Plotly
    fig = go.Figure()

    for name, data in compare_data:
        fig.add_trace(
            go.Scatter(
                x=data['dt'], 
                y=data['lots_count'], 
                mode='lines+markers',
                name=name
            )
        )

    fig.update_layout(
        title={'text': "📈 Trend Numero di Lotti", 'x': 0.1, 'font': {'size': 26}},
        xaxis_title='Data',
        yaxis_title='Prezzo Medio (£ GBP)',
        template='plotly_white',
        xaxis_tickangle=45,
        margin=dict(l=40, r=40, t=80, b=40),
        hovermode="x unified",
        legend_title_text="Distilleria",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Crea un secondo boxplot per il trading volume
    fig = go.Figure()

    for idx, (name, data) in enumerate(compare_data):
        fig.add_trace(
            go.Box(
                y=data['trading_volume'],
                name=name,
                marker_color=color_sequence[idx % len(color_sequence)],
                boxmean=True,  # Mostra anche la media
                boxpoints='outliers'  # Mostra solo gli outlier
            )
        )

    fig.update_layout(
        title={'text': "📊 Boxplot Trading Volume", 'x': 0.1, 'font': {'size': 26}},
        yaxis_title='Prezzo Medio (£ GBP)',
        xaxis_title='Distilleria',
        template='plotly_white',
        margin=dict(l=40, r=40, t=80, b=50),
        boxmode='group'
    )

    st.plotly_chart(fig, use_container_width=True)

# Funzione per visualizzare il ranking delle distillerie
def show_rankings(df_info, df_data):
    st.title("🏆 Classifiche")
    
    tab1, tab2, tab3 = st.tabs(["Rating", "Prezzo Medio", "Volume di Trading"])
    
    # Funzione comune per generare i box
    def create_bar(distilleria, valore, valore_massimo, colore_barra, colore_sfondo, simbolo_medaglia="", unità=""):
        bar_width = (valore / valore_massimo) * 100

        st.markdown(
            f"""
            <div style='
                background-color: {colore_sfondo};
                border-radius: 8px;
                padding: 8px 12px;
                margin-bottom: 8px;
                width: 100%;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
            '>
                <div style='
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 4px;
                    font-weight: bold;
                    font-size: 16px;
                    color: black;
                '>
                    <div style='text-align: left;'>{simbolo_medaglia} {distilleria}</div>
                    <div style='text-align: right;'>{valore:.2f} {unità}</div>
                </div>
                <div style='
                    background-color: {colore_barra};
                    width: {bar_width}%;
                    height: 20px;
                    border-radius: 6px;
                '></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Tab 1: Top distillerie per rating
    with tab1:
        st.subheader("⭐ Top 10 Distillerie per Rating")
        top_rating = df_info.sort_values(by='whiskybase_rating', ascending=False).head(10)
        max_rating = top_rating['whiskybase_rating'].max()
        medals = ["🥇", "🥈", "🥉"]

        for idx, (index, row) in enumerate(top_rating.iterrows()):
            distilleria = row['name']
            rating = row['whiskybase_rating']
            medal = medals[idx] if idx < 3 else ""
            create_bar(distilleria, rating, max_rating, colore_barra="#1F77B4", colore_sfondo="#E8F6F3", simbolo_medaglia=medal)

    # Tab 2: Top distillerie per prezzo medio
    with tab2:
        st.subheader("💰 Top 10 Distillerie per Prezzo Medio")
        avg_prices = df_data.groupby('name')['winning_bid_mean'].mean().reset_index()
        top_prices = avg_prices.sort_values(by='winning_bid_mean', ascending=False).head(10)
        max_price = top_prices['winning_bid_mean'].max()
        medals = ["🥇", "🥈", "🥉"]

        for idx, (index, row) in enumerate(top_prices.iterrows()):
            distilleria = row['name']
            prezzo_medio = row['winning_bid_mean']
            medal = medals[idx] if idx < 3 else ""
            create_bar(distilleria, prezzo_medio, max_price, colore_barra="#F4D03F", colore_sfondo="#FEF9E7", simbolo_medaglia=medal, unità="£")

    # Tab 3: Top distillerie per volume di trading
    with tab3:
        st.subheader("📊 Top 10 Distillerie per Volume di Trading")
        total_volume = df_data.groupby('name')['trading_volume'].sum().reset_index()
        top_volume = total_volume.sort_values(by='trading_volume', ascending=False).head(10)
        max_volume = top_volume['trading_volume'].max()
        medals = ["🥇", "🥈", "🥉"]

        for idx, (index, row) in enumerate(top_volume.iterrows()):
            distilleria = row['name']
            volume_totale = row['trading_volume']
            medal = medals[idx] if idx < 3 else ""
            create_bar(distilleria, volume_totale, max_volume, colore_barra="#E74C3C", colore_sfondo="#FDEDEC", simbolo_medaglia=medal, unità="£")

# App principale
def main():
    # Carica i dati
    df_info, df_data = load_data(top_n=50)
    
    if df_info.empty:
        st.error("Impossibile caricare i dati delle distillerie. Verifica la connessione e riprova.")
        return
    
    # Sidebar per la navigazione
    st.sidebar.title("🥃 Whisky Dashboard")
    
    # Menu di navigazione
    menu = st.sidebar.radio(
        "Menu di Navigazione",
        options=["Panoramica", "Classifiche", "Analisi Distillerie", "Confronto Distillerie"]
    )

    
    # Visualizza la pagina selezionata
    if menu == "Panoramica":
        show_overview(df_info, df_data)
    elif menu == "Analisi Distillerie":
        show_distillery_analysis(df_info, df_data)
    elif menu == "Confronto Distillerie":
        show_distillery_comparison(df_info, df_data)
    elif menu == "Classifiche":
        show_rankings(df_info, df_data)
    
    # Footer
    st.sidebar.divider()
    st.sidebar.info("Autrice: **Erica Cutuli**, PhD")
    st.sidebar.warning("Dati forniti da WhiskyHunter API")
    st.sidebar.caption("Progetto sviluppato all'interno del *Coding Bootcamp AI Engineer* di **Edgemony**")

if __name__ == "__main__":
    main()
