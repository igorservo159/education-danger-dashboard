# data_loader.py

# --- Informações do Dataset Limpo ---
# <class 'pandas.core.frame.DataFrame'>
# RangeIndex: 4607 entries, 0 to 4606
# Data columns (total 32 columns):
#  #   Column                                         Non-Null Count  Dtype         
# ---  ------                                         --------------  -----         
#  0   Date                                           4607 non-null   datetime64[ns]
#  1   Country                                        4607 non-null   object        
#  2   Country ISO                                    4607 non-null   object        
#  3   Admin 1                                        4607 non-null   object        
#  4   Latitude                                       3981 non-null   float64       
#  5   Longitude                                      3981 non-null   float64       
#  6   Geo Precision                                  4606 non-null   object        
#  7   Location of event                              4607 non-null   object        
#  8   Reported Perpetrator                           4607 non-null   object        
#  9   Reported Perpetrator Name                      4607 non-null   object        
#  10  Weapon Carried/Used                            4607 non-null   object        
#  11  Type of education facility                     4607 non-null   object        
#  12  Attacks on Schools                             4607 non-null   int64         
#  13  Attacks on Universities                        4607 non-null   int64         
#  14  Military Occupation of Education facility      4607 non-null   int64         
#  15  Arson attack on education facility             4607 non-null   int64         
#  16  Forced Entry into education facility           4607 non-null   int64         
#  17  Damage/Destruction To Ed facility Event        4607 non-null   int64         
#  18  Attacks on Students and Teachers               4607 non-null   bool          
#  19  Educators Killed                               4607 non-null   int64         
#  20  Educators Injured                              4607 non-null   int64         
#  21  Educators Kidnapped                            4607 non-null   int64         
#  22  Educators Arrested                             4607 non-null   int64         
#  23  Students Attacked in School                    4607 non-null   int64         
#  24  Students Killed                                4607 non-null   int64         
#  25  Students Injured                               4607 non-null   int64         
#  26  Students Kidnapped                             4607 non-null   int64         
#  27  Students Arrested                              4607 non-null   int64         
#  28  Sexual Violence Affecting School Age Children  4607 non-null   int64         
#  29  Year                                           4607 non-null   int32         
#  30  Month                                          4607 non-null   int32         
#  31  Total Victims                                  4607 non-null   int64         
# dtypes: bool(1), datetime64[ns](1), float64(2), int32(2), int64(17), object(9)
# memory usage: 1.1+ MB
#
# --- Primeiras 5 Linhas do Dataset Limpo ---
#         Date  Country Country ISO               Admin 1  Latitude  Longitude  \
# 0 2025-05-25  Ukraine         UKR      Chernihiv Oblast      51.4       31.2   
# 1 2025-05-24  Ukraine         UKR   Obolonskyi district      50.5       30.5   
# 2 2025-05-24  Ukraine         UKR  Dniprovskyi district      50.4       30.5   
# 3 2025-05-22  Ukraine         UKR        Donetsk Oblast      48.5       37.6   
# 4 2025-05-12  Ukraine         UKR           Sumy Oblast      50.9       34.2   
#
#           Geo Precision    Location of event       Reported Perpetrator  \
# 0  (2) 25 km Precision   Education Building   Foreign Forces - Military   
# 1  (2) 25 km Precision   Education Building   Foreign Forces - Military   
# 2  (2) 25 km Precision   Education Building   Foreign Forces - Military   
# 3  (2) 25 km Precision   Education Building                       Other   
# 4  (2) 25 km Precision   Education Building   Foreign Forces - Military   
#
#                 Reported Perpetrator Name  ... Educators Arrested  \
# 0  Armed Forces of the Russian Federation  ...                  0   
# 1  Armed Forces of the Russian Federation  ...                  0   
# 2  Armed Forces of the Russian Federation  ...                  0   
# 3                 Armed Forces of Ukraine  ...                  0   
# 4  Armed Forces of the Russian Federation  ...                  0   
#
#   Students Attacked in School  Students Killed  Students Injured  \
# 0                           0                0                 0   
# 1                           0                0                 0   
# 2                           0                0                 0   
# 3                           0                0                 0   
# 4                           0                0                 0   
#
#    Students Kidnapped  Students Arrested  \
# 0                   0                  0   
# 1                   0                  0   
# 2                   0                  0   
# 3                   0                  0   
# 4                   0                  0   
#
#    Sexual Violence Affecting School Age Children  Year  Month  Total Victims  
# 0                                              0  2025      5              0  
# 1                                              0  2025      5              0  
# 2                                              0  2025      5              0  
# 3                                              0  2025      5              0  
# 4                                              0  2025      5              0  
#
# [5 rows x 32 columns]
#
# /tmp/ipython-input-18-2041884838.py:18: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
#
# For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
#
#
#   df_clean['Admin 1'].fillna('Desconhecido', inplace=True)
# /tmp/ipython-input-18-2041884838.py:19: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
#
# For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
#
#
#   df_clean['Location of event'].fillna('Desconhecido', inplace=True)
#


import streamlit as st
import pandas as pd
import kagglehub
import os

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import silhouette_score

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
        'Educators Killed', 'Educators Injured', 'Educators Kidnapped', 'Educators Arrested',
        'Students Killed', 'Students Injured', 'Students Kidnapped', 'Students Arrested'
    ]
    df_clean['Total Victims'] = df_clean[victim_cols].sum(axis=1)
    
    # --- Totais de categorias relevantes ---
    df_clean['Total Killed'] = df_clean['Educators Killed'] + df_clean['Students Killed']
    df_clean['Total Injured'] = df_clean['Educators Injured'] + df_clean['Students Injured']
    df_clean['Total Kidnapped'] = df_clean['Educators Kidnapped'] + df_clean['Students Kidnapped']
    df_clean['Total Arrested'] = df_clean['Educators Arrested'] + df_clean['Students Arrested']

    return df_clean


def aplicar_clustering(df, n_clusters=4):
    df_cluster = df.copy()

    # Novas features relativas
    df_cluster['Pct_Killed'] = df_cluster['Total Killed'] / (df_cluster['Total Victims'] + 1)
    df_cluster['Pct_Injured'] = df_cluster['Total Injured'] / (df_cluster['Total Victims'] + 1)
    df_cluster['Pct_Kidnapped'] = df_cluster['Total Kidnapped'] / (df_cluster['Total Victims'] + 1)
    df_cluster['Pct_Arrested'] = df_cluster['Total Arrested'] / (df_cluster['Total Victims'] + 1)
    df_cluster['Pct_Sexual'] = df_cluster['Sexual Violence Affecting School Age Children'] / (df_cluster['Total Victims'] + 1)

    features = [
        'Pct_Killed', 'Pct_Injured', 'Pct_Kidnapped', 'Pct_Arrested', 'Pct_Sexual'
    ]

    transformer = ColumnTransformer([
        ('num', StandardScaler(), features),
    ])

    pipeline = Pipeline([
        ('transform', transformer),
        ('cluster', KMeans(n_clusters=n_clusters, random_state=42, n_init='auto'))
    ])

    cluster_labels = pipeline.fit_predict(df_cluster[features])
    df_cluster['Cluster'] = cluster_labels

    return df_cluster

def avaliar_clustering(df, labels, features_usadas):
    """
    Calcula o Silhouette Score com base nos dados e rótulos de cluster.
    """
    try:
        score = silhouette_score(df[features_usadas], labels)
        return round(score, 3)
    except Exception as e:
        return f"Erro ao calcular Silhouette Score: {e}"

