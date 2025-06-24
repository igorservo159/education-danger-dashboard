# dashboard.py (Solução Definitiva com Plotly + OpenStreetMap)

import streamlit as st
import pandas as pd
import plotly.express as px
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
paises_default_desejados = ["Ukraine", "Myanmar", "OPT", "Nigeria"]
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
    # Usamos px.scatter_mapbox, mas com um estilo que não requer token da Mapbox
    fig_map = px.scatter_mapbox(
        df_filtered,
        lat="Latitude",
        lon="Longitude",
        color="Total Victims",          # Cor baseada no número real de vítimas
        size="Total Victims",           # O tamanho dos círculos também representa as vítimas
        hover_name="Country",
        hover_data={"Admin 1": True, "Total Victims": True, "Year": True},
        color_continuous_scale=px.colors.sequential.Plasma, # Escala de cores vibrante
        size_max=50,  # Define o tamanho máximo dos círculos
        zoom=1.5 # Nível de zoom inicial
    )
    
    fig_map.update_layout(
        # AQUI ESTÁ A "MÁGICA": Usamos o mapa gratuito do OpenStreetMap como fundo.
        # Nenhuma chamada à API do Mapbox é feita, portanto, nenhum token é necessário.
        mapbox_style="open-street-map", 
        height=600,
        margin={"r":0,"t":20,"l":0,"b":0}
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para exibir o mapa com os filtros selecionados.")
