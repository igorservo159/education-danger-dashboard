# dashboard.py (Página Principal: Visão Geral)

import streamlit as st
import pandas as pd
import plotly.express as px
import os
# Importaremos a função de um arquivo separado para compartilhar entre as páginas
from data_loader import load_data 

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Visão Geral | Educação em Perigo")

# --- Carregamento dos Dados ---
# Tenta carregar os dados e mostra um erro amigável se falhar
try:
    df = load_data()
except Exception as e:
    st.error("Ocorreu um erro ao carregar e processar os dados.")
    st.error(f"Detalhe técnico do erro: {e}")
    st.info("Verifique se todas as dependências no `requirements.txt` estão corretas e se suas credenciais do Kaggle nos Secrets estão válidas.")
    st.stop()

# --- Título da Página ---
st.title("🌍 Dashboard: Análise de Incidentes na Educação")
st.markdown("Bem-vindo à análise de dados de incidentes que afetam a educação em zonas de conflito e crise (2020-2025).")
st.markdown("Use o menu à esquerda para navegar entre a **Visão Geral** e as **Análises Detalhadas**.")


# --- Barra Lateral de Filtros (Sidebar) ---
# Os filtros aqui afetarão APENAS esta página
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

# --- Aplicação dos Filtros ---
query_parts = []
if selected_countries:
    query_parts.append(f"Country in @selected_countries")
query_parts.append(f"Year >= {selected_year_range[0]} and Year <= {selected_year_range[1]}")
full_query = " and ".join(query_parts)
df_filtered = df.query(full_query)


# --- KPIs e Mapa ---
st.markdown("### Métricas Gerais (com base nos filtros)")

col1, col2, col3 = st.columns(3)
col1.metric("Total de Incidentes", f"{len(df_filtered):,}")
col2.metric("Total de Vítimas", f"{int(df_filtered['Total Victims'].sum()):,}")
col3.metric("Países Afetados", f"{df_filtered['Country'].nunique()}")

st.markdown("---")
st.subheader("Mapa de Distribuição de Incidentes")

if not df_filtered.empty:
    fig_map = px.scatter_geo(
        df_filtered,
        lat="Latitude",
        lon="Longitude",
        color="Total Victims",          # Cor baseada no número de vítimas
        hover_name="Country",           # O que aparece ao passar o mouse
        projection="natural earth",     # Tipo de projeção do globo
        hover_data={"Admin 1": True, "Total Victims": True, "Year": True},
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    # --- OTIMIZAÇÃO DO MAPA ---
    fig_map.update_geos(
        visible=False, # Oculta o globo base para focar nos pontos
        resolution=110, # Reduz a resolução dos contornos
        showcountries=True, landcolor="whitesmoke", countrycolor="darkgray"
    )
    
    fig_map.update_layout(
        height=500, # Tamanho fixo
        margin={"r":0,"t":20,"l":0,"b":0},
        # Desabilita o arraste e o zoom, mantendo o hover
        dragmode=False 
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados para exibir o mapa.")
