# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import kagglehub
import os

# --- Configuração da Página e Cache ---

# Configura o layout da página para ser "wide" (largo) e define um título
st.set_page_config(layout="wide", page_title="Dashboard: Educação em Perigo")

# Usa o cache do Streamlit para carregar os dados apenas uma vez, melhorando a performance
@st.cache_data
def load_data():
    """
    Função para baixar o dataset do Kaggle, carregar em um DataFrame
    e realizar a limpeza e pré-processamento iniciais.
    """
    # Baixar o dataset (requer autenticação do Kaggle configurada)
    path = kagglehub.dataset_download("mohamedramadan2040/education-in-danger-incident-data-2020-to2025")
    xlsx_path = os.path.join(path, "2020-2025-education-in-danger-incident-data.xlsx")
    df = pd.read_excel(xlsx_path)

    # --- Limpeza e Processamento dos Dados (do nosso EDA anterior) ---
    df_clean = df.copy()
    
    # Remover colunas desnecessárias
    cols_to_drop = [
        'Event Description', 'Known Educators Kidnap Or Arrest Outcome',
        'Known Student Kidnap Or Arrest Outcome', 'SiND Event ID'
    ]
    df_clean.drop(columns=cols_to_drop, inplace=True)

    # Preencher valores nulos
    df_clean['Admin 1'].fillna('Desconhecido', inplace=True)
    df_clean['Location of event'].fillna('Desconhecido', inplace=True)

    # Remover linhas onde a localização é nula para o mapa
    df_clean.dropna(subset=['Latitude', 'Longitude'], inplace=True)

    # Engenharia de Features
    df_clean['Year'] = df_clean['Date'].dt.year
    
    victim_cols = [
        'Educators Killed', 'Educators Injured', 'Educators Kidnapped',
        'Students Killed', 'Students Injured', 'Students Kidnapped'
    ]
    df_clean['Total Victims'] = df_clean[victim_cols].sum(axis=1)
    
    return df_clean

# Carrega os dados usando a função cacheada

try:
    df = load_data()
except Exception as e:
    # Mostra uma mensagem geral e em seguida o erro técnico exato.
    st.error("Ocorreu um erro ao carregar e processar os dados.")
    st.error(f"Detalhe técnico do erro: {e}")
    st.info("Verifique se todas as dependências no `requirements.txt` estão corretas (como `openpyxl` para ler arquivos Excel) e se suas credenciais do Kaggle nos Secrets estão válidas.")
    st.stop()


# --- Barra Lateral de Filtros (Sidebar) ---

st.sidebar.header("Filtros Interativos")

# Filtro de País (Multiseleção)
# Pega os países únicos e ordena
paises_sorted = sorted(df['Country'].unique())

# Define a lista de países que gostaríamos de ter como padrão
paises_default_desejados = ["Ukraine", "Myanmar", "OPT", "Nigeria"]

# Cria a lista de defaults válidos, checando quais dos desejados realmente existem nos dados
paises_default_validos = [p for p in paises_default_desejados if p in paises_sorted]

# Usa a lista de defaults válidos no widget
selected_countries = st.sidebar.multiselect(
    "Selecione o(s) País(es)",
    options=paises_sorted,
    default=paises_default_validos # Usa a nova lista robusta
)

# Filtro de Ano (Slider de intervalo)
min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
selected_year_range = st.sidebar.slider(
    "Selecione o Intervalo de Anos",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year) # Padrão para todo o intervalo
)

# Filtro de Perpetrador (Multiseleção)
perpetradores_sorted = sorted(df['Reported Perpetrator'].unique())
selected_perpetrators = st.sidebar.multiselect(
    "Selecione o(s) Perpetrador(es)",
    options=perpetradores_sorted,
    default=perpetradores_sorted # Padrão para todos
)


# --- Aplicação dos Filtros no DataFrame ---

# Filtra o DataFrame com base nas seleções da barra lateral
# Usando o método .query() do pandas para uma filtragem limpa
query_parts = []
if selected_countries:
    query_parts.append(f"Country in @selected_countries")
if selected_perpetrators:
    query_parts.append(f"`Reported Perpetrator` in @selected_perpetrators")
query_parts.append(f"Year >= {selected_year_range[0]} and Year <= {selected_year_range[1]}")

# Junta todas as partes da query com 'and'
full_query = " and ".join(query_parts)
df_filtered = df.query(full_query)


# --- Corpo Principal do Dashboard ---

st.title("🌍 Dashboard: Análise de Incidentes na Educação")
st.markdown("Este dashboard interativo apresenta os insights da análise de dados de incidentes que afetam a educação em zonas de conflito e crise (2020-2025).")

# --- KPIs (Key Performance Indicators) ---
st.markdown("### Métricas Gerais (com base nos filtros)")

# Cria 3 colunas para as métricas
col1, col2, col3 = st.columns(3)
total_incidentes = len(df_filtered)
total_vitimas = int(df_filtered['Total Victims'].sum())
paises_afetados = df_filtered['Country'].nunique()

col1.metric("Total de Incidentes", f"{total_incidentes:,}")
col2.metric("Total de Vítimas", f"{total_vitimas:,}")
col3.metric("Países Afetados", f"{paises_afetados}")


st.markdown("---")

# --- Mapa de Incidentes ---
st.subheader("Mapa de Calor e Distribuição de Incidentes")
st.markdown("Use o mouse para navegar e ampliar. O tamanho e a cor dos pontos indicam o número de vítimas.")

st.subheader("Mapa de Distribuição de Incidentes")
st.markdown("Use o mouse para navegar e ampliar.")

if not df_filtered.empty:
    fig_map = px.scatter_geo(
        df_filtered,
        lat="Latitude",
        lon="Longitude",
        color="Total Victims",          # Cor baseada no número de vítimas
        size="Total Victims",           # Tamanho baseado no número de vítimas
        hover_name="Country",           # O que aparece ao passar o mouse
        projection="natural earth",     # Tipo de projeção do globo
        title="Distribuição Geográfica de Incidentes",
        hover_data={"Admin 1": True, "Total Victims": True, "Year": True},
        color_continuous_scale=px.colors.sequential.Reds # Escala de cores
    )
    
    fig_map.update_geos(
        showcountries=True,
        showcoastlines=True,
        coastlinecolor="RebeccaPurple",
        showland=True,
        landcolor="LightGreen",
        showocean=True,
        oceancolor="LightBlue"
    )

    fig_map.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0})
    
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados para exibir o mapa.")

# --- Gráficos em Colunas ---
st.subheader("Análises Detalhadas por Categoria")
col1, col2 = st.columns(2)

with col1:
    # Gráfico de barras: Top 10 Países
    st.markdown("##### Incidentes por País")
    if not df_filtered.empty:
        country_counts = df_filtered['Country'].value_counts().head(10).sort_values(ascending=True)
        fig_countries = px.bar(country_counts, x=country_counts.values, y=country_counts.index, orientation='h', text_auto=True)
        fig_countries.update_layout(xaxis_title="Nº de Incidentes", yaxis_title="País")
        st.plotly_chart(fig_countries, use_container_width=True)
    else:
        st.warning("Nenhum dado de país para os filtros.")

with col2:
    # Gráfico de barras: Top 10 Perpetradores
    st.markdown("##### Incidentes por Perpetrador")
    if not df_filtered.empty:
        perp_counts = df_filtered['Reported Perpetrator'].value_counts().head(10).sort_values(ascending=True)
        fig_perps = px.bar(perp_counts, x=perp_counts.values, y=perp_counts.index, orientation='h', text_auto=True)
        fig_perps.update_layout(xaxis_title="Nº de Incidentes", yaxis_title="Perpetrador")
        st.plotly_chart(fig_perps, use_container_width=True)
    else:
        st.warning("Nenhum dado de perpetrador para os filtros.")


# --- Gráfico de Série Temporal ---
st.subheader("Evolução dos Incidentes ao Longo do Tempo")
if not df_filtered.empty:
    df_filtered['Month_Year'] = df_filtered['Date'].dt.to_period('M').astype(str)
    time_series_counts = df_filtered.groupby('Month_Year').size().reset_index(name='Count')
    fig_time = px.line(time_series_counts, x='Month_Year', y='Count', markers=True)
    fig_time.update_layout(xaxis_title="Mês/Ano", yaxis_title="Nº de Incidentes")
    st.plotly_chart(fig_time, use_container_width=True)
else:
    st.warning("Nenhum dado temporal para os filtros.")
