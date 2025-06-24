# pages/1_Análises_Detalhadas.py

import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data # Importa a mesma função de carregamento

# --- Configuração da Página e Carregamento de Dados ---
st.set_page_config(layout="wide", page_title="Análises | Educação em Perigo")
df = load_data() # Usa a função cacheada

# --- Título da Página ---
st.title("📊 Análises Detalhadas")
st.markdown("Explore os dados de incidentes com visualizações detalhadas.")

# --- Filtros (Aplicados a todos os gráficos desta página) ---
st.sidebar.header("Filtros para Análises")
paises_sorted = sorted(df['Country'].unique())
selected_countries_details = st.sidebar.multiselect(
    "País(es) para Análise",
    options=paises_sorted,
    default=paises_sorted # Começa com todos selecionados
)
df_filtered = df[df['Country'].isin(selected_countries_details)]

# --- Layout dos Gráficos ---

# GRÁFICOS QUE FALTAVAM
st.markdown("### Tipos de Incidentes e Severidade")
col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Contagem por Tipo de Incidente")
    incident_type_cols = [
        'Attacks on Schools', 'Attacks on Universities',
        'Military Occupation of Education facility', 'Arson attack on education facility',
        'Forced Entry into education facility', 'Damage/Destruction To Ed facility Event',
        'Attacks on Students and Teachers'
    ]
    incident_counts = df_filtered[incident_type_cols].sum().sort_values(ascending=False)
    fig_types = px.bar(incident_counts, x=incident_counts.values, y=incident_counts.index, text_auto=True, orientation='h')
    fig_types.update_layout(showlegend=False, yaxis_title=None, xaxis_title="Nº de Incidentes")
    st.plotly_chart(fig_types, use_container_width=True)

with col2:
    st.markdown("##### Severidade por Tipo de Ataque")
    severity_by_type = {}
    for col in incident_type_cols:
        avg_victims = df_filtered[df_filtered[col] > 0]['Total Victims'].mean()
        severity_by_type[col.replace(" facility", "").split(" ")[0]] = avg_victims
    severity_df = pd.DataFrame(list(severity_by_type.items()), columns=['Tipo', 'Média de Vítimas']).sort_values('Média de Vítimas')
    fig_severity = px.bar(severity_df, x='Média de Vítimas', y='Tipo', text_auto='.2f', orientation='h')
    fig_severity.update_layout(yaxis_title=None, xaxis_title="Média de Vítimas por Incidente")
    st.plotly_chart(fig_severity, use_container_width=True)

st.markdown("---")
st.markdown("### Custo Humano e Armamento Utilizado")
col3, col4 = st.columns(2)

with col3:
    st.markdown("##### Custo Humano Total")
    victim_cols = [
        'Educators Killed', 'Educators Injured', 'Educators Kidnapped',
        'Students Killed', 'Students Injured', 'Students Kidnapped'
    ]
    human_cost = df_filtered[victim_cols].sum().sort_values(ascending=False)
    fig_hc = px.bar(human_cost, x=human_cost.index, y=human_cost.values, text_auto=True)
    fig_hc.update_layout(xaxis_title="Tipo de Vítima", yaxis_title="Contagem Total")
    st.plotly_chart(fig_hc, use_container_width=True)
    
with col4:
    st.markdown("##### Armamento Utilizado (Top 10)")
    weapon_counts = df_filtered['Weapon Carried/Used'].value_counts().head(10)
    fig_weapons = px.pie(weapon_counts, names=weapon_counts.index, values=weapon_counts.values, hole=0.3)
    fig_weapons.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_weapons, use_container_width=True)

st.markdown("---")
st.markdown("### Análise Cruzada: País vs. Perpetrador")
st.markdown("Este gráfico mostra a proporção de tipos de perpetradores para os 5 países com mais incidentes (com base nos filtros atuais).")

if not df_filtered.empty:
    top_5_countries_list = df_filtered['Country'].value_counts().head(5).index
    df_top5 = df_filtered[df_filtered['Country'].isin(top_5_countries_list)]
    country_perp_crosstab = pd.crosstab(df_top5['Country'], df_top5['Reported Perpetrator'])
    crosstab_norm = country_perp_crosstab.div(country_perp_crosstab.sum(axis=1), axis=0) * 100
    
    fig_cross = px.bar(crosstab_norm, orientation='h', text_auto='.2f', title="Proporção de Perpetradores por País (%)")
    fig_cross.update_layout(xaxis_title="Percentual de Incidentes (%)", yaxis_title="País", legend_title="Perpetrador")
    st.plotly_chart(fig_cross, use_container_width=True)
