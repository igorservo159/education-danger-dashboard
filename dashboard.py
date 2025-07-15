import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from data_loader import load_data, aplicar_clustering, avaliar_clustering

st.set_page_config(layout="wide", page_title="Visão Geral | Educação em Perigo")

# --- Carregamento dos dados ---
try:
    df = load_data()
except Exception as e:
    st.error("Ocorreu um erro ao carregar e processar os dados.")
    st.error(f"Detalhe técnico do erro: {e}")
    st.stop()

st.title("🌍 Dashboard: Análise de Incidentes na Educação")
st.markdown("Bem-vindo à análise de dados de incidentes que afetam a educação (2020-2025).")
st.markdown("Use o menu à esquerda para navegar entre a **Visão Geral** e as **Análises Detalhadas**.")

# --- Filtros principais ---
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

# --- Filtro de dados ---
query_parts = []
if selected_countries:
    query_parts.append(f"Country in @selected_countries")
else: 
    query_parts.append("Country == Country")

query_parts.append(f"Year >= {selected_year_range[0]} and Year <= {selected_year_range[1]}")
full_query = " and ".join(query_parts)
df_filtered = df.query(full_query)

# --- Clustering (impacto_vitimas) ---
st.sidebar.header("Clustering (Agrupamento)")
usar_clustering = st.sidebar.checkbox("Ativar Clustering")
num_clusters = st.sidebar.slider("Número de Grupos", 2, 50, 4)

if usar_clustering:
    try:
        estrategia = "impacto_vitimas"
        df_filtered = aplicar_clustering(df_filtered, n_clusters=num_clusters)
        df_filtered['Cluster'] = df_filtered['Cluster'].astype(str)

        features_usadas = [
            "Total Killed", "Total Injured", "Total Kidnapped",
            "Total Arrested", "Sexual Violence Affecting School Age Children"
        ]
        df_encoded = df_filtered[features_usadas]

        score = avaliar_clustering(df_encoded, df_filtered['Cluster'], df_encoded.columns)
        st.sidebar.info(f"Silhouette Score: **{score}**")
    except Exception as e:
        st.warning(f"Erro ao aplicar clustering: {e}")
        usar_clustering = False

# --- Métricas Gerais ---
st.markdown("### Métricas Gerais (com base nos filtros)")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Incidentes", f"{len(df_filtered):,}")
col2.metric("Total de Vítimas", f"{int(df_filtered['Total Victims'].sum()):,}")
col3.metric("Países Afetados", f"{df_filtered['Country'].nunique()}")

# --- Mapa Interativo ---
st.markdown("---")
st.subheader("Mapa Interativo de Incidentes")
st.markdown("Use o scroll do mouse para dar zoom e clique e arraste para navegar.")

if not df_filtered.empty:
    center_lat = df_filtered.iloc[0]['Latitude'] if selected_countries else 25
    center_lon = df_filtered.iloc[0]['Longitude'] if selected_countries else 10
    zoom_level = 3 if selected_countries else 2

    df_plot = df_filtered.copy()
    df_plot['Marker Size'] = np.where(df_plot['Total Victims'] == 0, 10, df_plot['Total Victims'] + 10)

    hover_cols = {
        "Admin 1": True,
        "Reported Perpetrator Name": True,
        "Weapon Carried/Used": True,
        "Total Victims": True,
        "Total Killed": True,
        "Total Arrested": True,
        "Total Kidnapped": True,
        "Total Injured": True,
        "Sexual Violence Affecting School Age Children": True,
        "Latitude": False,
        "Longitude": False,
        "Marker Size": False,
    }

    if usar_clustering and "Cluster" in df_plot.columns:
        hover_cols["Cluster"] = True

    fig_map = px.scatter_mapbox(
        df_plot,
        lat="Latitude",
        lon="Longitude",
        color="Cluster" if usar_clustering and "Cluster" in df_plot.columns else "Total Victims",
        size="Marker Size",
        hover_name="Country",
        hover_data=hover_cols,
        color_continuous_scale="Viridis" if not usar_clustering else None,
        size_max=50,
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

# --- Gráficos por Cluster ---
if usar_clustering and "Cluster" in df_filtered.columns:
    st.markdown("---")
    st.subheader("📊 Análise por Cluster")

    st.markdown("**Soma dos Impactos por Cluster**")
    df_impacto_grouped = df_filtered.groupby("Cluster").sum(numeric_only=True).reset_index()
    df_impacto_grouped = df_impacto_grouped[[
        "Cluster", "Total Killed", "Total Injured", "Total Kidnapped", "Total Arrested",
        "Sexual Violence Affecting School Age Children"
    ]].rename(columns={
        "Sexual Violence Affecting School Age Children": "Sexual Violence"
    })

    st.markdown("**Distribuição Detalhada por Tipo de Impacto**")

    colunas_impacto = [
        "Total Killed",
        "Total Injured",
        "Total Kidnapped",
        "Total Arrested",
        "Sexual Violence Affecting School Age Children"
    ]

    for col in colunas_impacto:
        fig = px.box(
            df_filtered,
            x="Cluster",
            y=col,
            title=f"{col} por Cluster",
            labels={"Cluster": "Grupo (Cluster)", col: "Quantidade"}
        )
        st.plotly_chart(fig, use_container_width=True)


    df_impacto_melted = df_impacto_grouped.melt(
        id_vars="Cluster",
        var_name="Categoria",
        value_name="Total"
    )

    fig_impacto = px.bar(
        df_impacto_melted,
        x="Categoria",
        y="Total",
        color="Cluster",
        barmode="group",
        title="Comparativo de Impacto por Cluster"
    )
    st.plotly_chart(fig_impacto, use_container_width=True)

    # --- Texto explicativo ---
    st.markdown("---")
    st.subheader("🧠 Interpretação dos Grupos (Clusters)")
    st.markdown("""
O clustering foi aplicado com o objetivo de **identificar padrões latentes** nos incidentes registrados.

### 💥 Agrupamento por Impacto nas Vítimas
Agrupa incidentes com base em **dados quantitativos**:
- Mortes, feridos, sequestros, prisões
- Ocorrência de violência sexual

Esse agrupamento destaca **a severidade dos ataques**, permitindo identificar os clusters mais letais ou violentos.

### 💡 Possíveis insights:
- Regiões com **maior impacto humano** podem demandar mais intervenção humanitária.
- Certos clusters podem representar **ameaças latentes**.
- Permite traçar **prioridades de resposta** com base no impacto real.

Essas análises ajudam governos, ONGs e pesquisadores a tomarem **decisões baseadas em dados**.

### 🧠 O que é Clustering (Agrupamento)?

Clustering é uma técnica **não supervisionada** que tenta **agrupar dados semelhantes** entre si, sem usar rótulos de verdade. O modelo tenta encontrar **padrões intrínsecos** na distribuição dos dados.

Nesse caso, o clustering tenta responder:

> *"Quais incidentes se parecem entre si com base no impacto sobre as vítimas?"*

### ⚙️ Como funciona o KMeans (que você está usando)

1. Escolhe `k` centróides iniciais (aleatoriamente ou por heurística).
2. Atribui cada ponto ao centróide mais próximo → forma k grupos.
3. Atualiza os centróides com base na média dos pontos do grupo.
4. Repete passos 2 e 3 até:
    * Os centróides não mudarem muito (convergência).
    * Ou atingir número máximo de iterações.

### 🔬 O que é o Silhouette Score?

O Silhouette Score mede o quão bem separado e coeso está cada grupo:
* Varia entre -1 e 1.
* Próximo de 1.0: os pontos estão bem agrupados e bem separados dos outros grupos.
* Próximo de 0.0: os grupos estão se sobrepondo.
* Valor negativo: os pontos estão no grupo errado.
""")
