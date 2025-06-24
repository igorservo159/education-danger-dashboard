# dashboard.py (Página Principal: Visão Geral - ATUALIZADO)

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np  # Importamos numpy para a escala logarítmica
from data_loader import load_data 

st.set_page_config(layout="wide", page_title="Visão Geral | Educação em Perigo")

try:
    df = load_data()
except Exception as e:
    st.error("Ocorreu um erro ao carregar os dados.")
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
st.subheader("Mapa de Distribuição de Incidentes")

if not df_filtered.empty:
    # --- MUDANÇA 2: MELHORANDO AS CORES DO MAPA ---
    # Usamos uma escala logarítmica para dar mais destaque a valores menores.
    # np.log1p(x) é o mesmo que np.log(1+x), para evitar erros com valores zero.
    df_plot = df_filtered.copy()
    df_plot['Log Victims'] = np.log1p(df_plot['Total Victims'])

    fig_map = px.scatter_geo(
        df_plot,
        lat="Latitude",
        lon="Longitude",
        color="Log Victims",  # Cor baseada na escala logarítmica
        hover_name="Country",
        projection="natural earth",
        # No hover, mostramos o número real de vítimas
        hover_data={"Admin 1": True, "Total Victims": True, "Log Victims": False},
        color_continuous_scale=px.colors.sequential.Plasma, # Uma escala de cores mais vibrante
        title="A cor representa a intensidade de vítimas (escala logarítmica)"
    )
    
    fig_map.update_geos(
        visible=True, 
        resolution=110,
        showcountries=True, landcolor="#F0F0F0", countrycolor="darkgray"
    )
    
    fig_map.update_layout(
        height=500,
        margin={"r":0,"t":40,"l":0,"b":0"},
        dragmode=False 
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para exibir o mapa com os filtros selecionados.")
