import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

st.title('Dashboard de Vendas')

@st.cache_data
def carregar_dados():
    df = pd.read_csv('vendas.csv')
    df['Data'] = pd.to_datetime(df['Data'])
    return df


df = carregar_dados()
st.sidebar.title('Filtros')

lista_de_categorias = sorted(df['Categoria'].unique())

categorias_selecionadas = st.sidebar.multiselect(
    'Selecione categorias',
    options=lista_de_categorias,
    default=lista_de_categorias 
)

data_min, data_max = df['Data'].min(), df['Data'].max()
periodo = st.sidebar.date_input(
    'Período',
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

if categorias_selecionadas:
    df_filtrado = df[df['Categoria'].isin(categorias_selecionadas)]
else:
    df_filtrado = df.iloc[0:0]

if isinstance(periodo, tuple) and len(periodo) == 2:
    inicio, fim = pd.to_datetime(periodo[0]), pd.to_datetime(periodo[1])
    df_filtrado = df_filtrado[(df_filtrado['Data'] >= inicio) & (df_filtrado['Data'] <= fim)]

col1, col2 = st.columns([1, 1])

receita_calculada = df_filtrado['Receita'].sum()
total_pedidos = df_filtrado['PedidoID'].nunique()

with col1:
    st.metric(label='Receita total', value=f"R$ {receita_calculada:,.2f}")

with col2:
    st.metric(label='Total pedidos', value=f"{total_pedidos}")

aba1, aba2 = st.tabs(['Evolução Mensal', 'Tabela de Dados'])

with aba1:
    if df_filtrado.empty:
        st.warning('Nenhum dado para exibir com os filtros atuais.')
    else:
        dados_agrupados = (
            df_filtrado
            .set_index('Data')
            .resample('ME')['Receita']
            .sum()
        )
        dados_agrupados.index = dados_agrupados.index.strftime('%Y-%m')
        st.area_chart(dados_agrupados)

with aba2:
    st.dataframe(df_filtrado, use_container_width=True)

    csv_para_download = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label='Baixar dados filtrados (CSV)',
        data=csv_para_download,
        file_name='vendas_filtradas.csv',
        mime='text/csv'
    )
