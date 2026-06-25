import streamlit as st
import pandas as pd
import json

# Configuração da página Web
st.set_page_config(page_title="MVP - Inteligência de Mercado", layout="wide")
st.title("Dashboard de Análise de Preços de Mercado")
st.markdown("Protótipo de Visão Computacional (OCR) + LLM para Estruturação de Prateleiras")

# Carregar o ficheiro JSON criado pela IA
@st.cache_data
def load_data():
    with open("catalogo_final.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)

try:
    df = load_data()
    
    # 1. Cartões de KPIs Superiores
    st.subheader("Métricas em Tempo Real")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Produtos Lidos", len(df))
    with col2:
        promo_count = df[df['promocao'] == True].shape[0]
        st.metric("Itens em Promoção", promo_count)
    with col3:
        preco_medio = df['preco'].mean()
        st.metric("Preço Médio Unitário", f"R$ {preco_medio:.2f}".replace('.', ','))
    with col4:
        st.metric("Volume Base", "2L predominante")

    st.markdown("---")
    left_column, right_column = st.columns([1, 1])

    # 2. Tabela Dinâmica do Catálogo
    with left_column:
        st.subheader(" Catálogo Estruturado")
        df_view = df.copy()
        # Formatação de campos para exibição amigável
        df_view['preco'] = df_view['preco'].apply(lambda x: f"R$ {x:.2f}".replace('.', ','))
        df_view['promocao'] = df_view['promocao'].apply(lambda x: " Sim" if x else "Não")
        st.dataframe(df_view, use_container_width=True)

    # 3. Gráfico de Barras para Análise Visual
    with right_column:
        st.subheader(" Comparativo de Preços")
        # Ordenar produtos para o gráfico do mais barato ao mais caro
        df_chart = df.sort_values(by='preco', ascending=True)
        st.bar_chart(df_chart.set_index('produto')['preco'], color="#1F4E78")

except FileNotFoundError:
    st.error("Ficheiro 'catalogo_final.json' não encontrado. Certifique-se de correr o script do Gemini primeiro.")
