# dashboard.py (Versão Final com Tamanho Mínimo para Marcadores)

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np # Adicionado para usar funções do numpy
from data_loader import load_data 

st.set_page_config(layout="wide", page_title="Visão Geral | Educação em Perigo")

try:
    df = load_data()
except Exception as e:
    st.error("Ocorreu um erro ao carregar e processar os dados.")
    st.error(f"Detalhe técnico do erro: {e}")
    st.stop()

st.title("🌍 Dashboard: Análise de Incidentes na Educação")
st.markdown("Bem-vindo à análise de dados de incidentes que afetam a educação (2020-2025).")
st.markdown("Use o menu à esquerda para navegar entre a **Visão Geral** e as **Análises Detalhadas**.")

st.sidebar.header("Filtros para Visão Geral")
paises_sorted = sorted(df['Country'].unique())
paises_default_desejados = ["Nigeria"] 
paises_default_validos = [p for p in paises_default_desejados if p in paises_sorted]
selected_countries = st.sidebar.multiselect(
    "Selecione o(s) País(es)", options=paises_sorted, default=paises_default_validos
)

min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
selected_year_range = st.sidebar.slider(
    "Selecione o Intervalo de Anos", min_value=min_year, max_value=max_year, value=(min_year, max_year)
)

query_parts = []
if selected_countries:
    query_parts.append(f"Country in @selected_countries")
else: 
    query_parts.append("Country == Country")

query_parts.append(f"Year >= {selected_year_range[0]} and Year <= {selected_year_range[1]}")
full_query = " and ".join(query_parts)
df_filtered = df.query(full_query)

st.markdown("### Métricas Gerais (com base nos filtros)")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Incidentes", f"{len(df_filtered):,}")
col2.metric("Total de Vítimas", f"{int(df_filtered['Total Victims'].sum()):,}")
col3.metric("Países Afetados", f"{df_filtered['Country'].nunique()}")


st.markdown("---")
st.subheader("Mapa Interativo de Incidentes")
st.markdown("Use o scroll do mouse para dar zoom e clique e arraste para navegar.")

if not df_filtered.empty:
    # LÓGICA PARA CENTRALIZAÇÃO E ZOOM DINÂMICOS
    if selected_countries:
        center_lat = df_filtered.iloc[0]['Latitude']
        center_lon = df_filtered.iloc[0]['Longitude']
        zoom_level = 3
    else: 
        center_lat = 25
        center_lon = 10
        zoom_level = 2

    # --- MUDANÇA AQUI: Criando a coluna de tamanho mínimo ---
    df_plot = df_filtered.copy()
    # Se 'Total Victims' for 0, usa 0.5. Caso contrário, usa o valor real.
    # Isso garante que todos os pontos sejam visíveis.
    df_plot['Marker Size'] = np.where(df_plot['Total Victims'] == 0, 2, df_plot['Total Victims'])

    fig_map = px.scatter_mapbox(
        df_plot, # Usamos o novo dataframe df_plot
        lat="Latitude",
        lon="Longitude",
        color="Total Victims",
        size="Marker Size", # Usamos a nova coluna para o tamanho
        hover_name="Country",
        hover_data={"Admin 1": True, "Total Victims": True, "Year": True},
        color_continuous_scale=px.colors.sequential.Plasma,
        size_max=40,
        zoom=zoom_level
    )
    
    fig_map.update_layout(
        mapbox_style="open-street-map", 
        mapbox_center={"lat": center_lat, "lon": center_lon},
        height=600,
        margin={"r":0,"t":20,"l":0,"b":0}
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para exibir o mapa com os filtros selecionados.")
