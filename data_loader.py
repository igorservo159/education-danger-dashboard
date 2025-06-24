# data_loader.py

import streamlit as st
import pandas as pd
import kagglehub
import os

@st.cache_data
def load_data():
    """
    Função para baixar o dataset do Kaggle, carregar em um DataFrame
    e realizar a limpeza e pré-processamento iniciais.
    Esta função é cacheada para alta performance entre as páginas.
    """
    # Baixar o dataset (requer autenticação do Kaggle configurada)
    path = kagglehub.dataset_download("mohamedramadan2040/education-in-danger-incident-data-2020-to2025")
    xlsx_path = os.path.join(path, "2020-2025-education-in-danger-incident-data.xlsx")
    df = pd.read_excel(xlsx_path, engine='openpyxl')

    # --- Limpeza e Processamento dos Dados ---
    df_clean = df.copy()
    
    cols_to_drop = [
        'Event Description', 'Known Educators Kidnap Or Arrest Outcome',
        'Known Student Kidnap Or Arrest Outcome', 'SiND Event ID'
    ]
    df_clean.drop(columns=cols_to_drop, inplace=True)

    df_clean['Admin 1'].fillna('Desconhecido', inplace=True)
    df_clean['Location of event'].fillna('Desconhecido', inplace=True)
    df_clean.dropna(subset=['Latitude', 'Longitude'], inplace=True)

    df_clean['Year'] = df_clean['Date'].dt.year
    
    victim_cols = [
        'Educators Killed', 'Educators Injured', 'Educators Kidnapped',
        'Students Killed', 'Students Injured', 'Students Kidnapped'
    ]
    df_clean['Total Victims'] = df_clean[victim_cols].sum(axis=1)
    
    return df_clean
