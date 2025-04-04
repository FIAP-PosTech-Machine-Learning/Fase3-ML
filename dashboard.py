import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração do Seaborn
sns.set(style="whitegrid")

# Título do Dashboard
st.title("Dashboard de Resultados - Modelos de Regressão")

# Função para carregar os dados
@st.cache
def load_data():
    file_path = r'C:\Users\vfanj\Documents\FIAP_POS_ML\Fase03_Tech_Challenge\bovespa-data-analysis\bovespa-data-analysis\resultados\model_results.csv'
    return pd.read_csv(file_path)

# Carregar os dados
data = load_data()

# Verificar os dados carregados
st.write("### Dados Carregados")
st.dataframe(data.head())

# Converter a coluna 'Date' para o formato de data
if 'Date' in data.columns:
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

# Exibir os filtros no menu lateral
st.sidebar.header("Filtros")
st.sidebar.write("Use os filtros abaixo para explorar os resultados.")

# Filtro por modelo
modelos = ["Todos"] + list(data['Modelo'].unique())
modelo_selecionado = st.sidebar.selectbox("Selecione o Modelo", modelos)

# Filtro por código de ação
codigos = ["Todos"] + list(data['Codigo'].unique())
codigo_selecionado = st.sidebar.selectbox("Selecione o Código de Ação", codigos)

# Filtro de data
if 'Date' in data.columns:
    st.sidebar.write("### Filtro de Data")
    filtro_data = st.sidebar.radio("Deseja filtrar por data?", ["Sem Data", "Com Data"])
    if filtro_data == "Com Data":
        data_inicio = st.sidebar.date_input("Data Início", value=data['Date'].min())
        data_fim = st.sidebar.date_input("Data Fim", value=data['Date'].max())
        data = data[(data['Date'] >= pd.Timestamp(data_inicio)) & (data['Date'] <= pd.Timestamp(data_fim))]

# Filtrar os dados com base nos filtros selecionados
dados_filtrados = data.copy()
if modelo_selecionado != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['Modelo'] == modelo_selecionado]
if codigo_selecionado != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['Codigo'] == codigo_selecionado]

# Exibir os dados filtrados
st.write("### Dados Filtrados")
st.dataframe(dados_filtrados)

# Gráfico de dispersão: Valores reais vs. preditos
if not dados_filtrados.empty:
    st.write("### Gráfico de Dispersão: Valores Reais vs. Preditos")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=dados_filtrados, x='Y_True', y='Y_Predicted', alpha=0.7)
    plt.plot([dados_filtrados['Y_True'].min(), dados_filtrados['Y_True'].max()],
             [dados_filtrados['Y_True'].min(), dados_filtrados['Y_True'].max()], 'r--')
    plt.xlabel("Valores Reais")
    plt.ylabel("Valores Preditos")
    plt.title("Valores Reais vs. Preditos")
    st.pyplot(plt)
else:
    st.write("Nenhum dado disponível para o gráfico de dispersão.")

# Gráfico de linha: Predições ao longo do tempo
if not dados_filtrados.empty and 'Date' in dados_filtrados.columns:
    st.write("### Gráfico de Linha: Predições ao Longo do Tempo")
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=dados_filtrados, x='Date', y='Y_True', label='Valores Reais', marker='o')
    sns.lineplot(data=dados_filtrados, x='Date', y='Y_Predicted', label='Valores Preditos', marker='o')
    plt.xticks(rotation=45)
    plt.xlabel("Data")
    plt.ylabel("Valores")
    plt.title("Predições ao Longo do Tempo")
    st.pyplot(plt)
else:
    st.write("Nenhum dado disponível ou a coluna 'Date' não está presente.")

# Comparação de métricas entre os modelos
st.write("### Comparação de Métricas entre os Modelos")
metricas = data.groupby('Modelo')[['MSE', 'R²', 'MAE', 'MAPE']].mean().reset_index()
st.dataframe(metricas)

# Gráfico de barras para comparar métricas
st.write("### Comparação de Métricas entre os Modelos")
metricas_melted = metricas.melt(id_vars='Modelo', var_name='Métrica', value_name='Valor')
plt.figure(figsize=(12, 6))
sns.barplot(data=metricas_melted, x='Métrica', y='Valor', hue='Modelo', palette='viridis')
plt.title("Comparação de Métricas entre os Modelos")
plt.ylabel("Valor")
plt.xlabel("Métrica")
st.pyplot(plt)

# Gráfico de distribuição de erros
if not dados_filtrados.empty:
    st.write("### Distribuição de Erros (|Y_True - Y_Predicted|)")
    dados_filtrados['Erro_Absoluto'] = abs(dados_filtrados['Y_True'] - dados_filtrados['Y_Predicted'])
    plt.figure(figsize=(10, 6))
    sns.histplot(dados_filtrados['Erro_Absoluto'], kde=True, bins=30, color='blue')
    plt.title("Distribuição de Erros Absolutos")
    plt.xlabel("Erro Absoluto")
    plt.ylabel("Frequência")
    st.pyplot(plt)

# Mapa de calor para ações com maior projeção
if 'Date' in data.columns:
    st.write("### Mapa de Calor: Ações com Maior Projeção")
    heatmap_data = data.pivot_table(index='Codigo', columns='Date', values='Y_Predicted', aggfunc='mean')
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap='coolwarm', annot=False, cbar_kws={'label': 'Projeção'})
    plt.title("Mapa de Calor: Projeção por Ação e Data")
    st.pyplot(plt)