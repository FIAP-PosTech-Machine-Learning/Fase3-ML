import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configurações da página
st.set_page_config(
    page_title="Análise de Modelos - B3", 
    page_icon="📈", 
    layout="wide"
)

# Função para carregar os dados com cache
@st.cache_data
def load_data():
    file_path = r'C:\Users\vfanj\Documents\FIAP_POS_ML\Fase03_Tech_Challenge\bovespa-data-analysis\bovespa-data-analysis\resultados\model_results.csv'
    df = pd.read_csv(file_path)
    
    # Transformações
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Calcular métricas adicionais
    df['Erro_Absoluto'] = (df['Y_Predicted'] - df['Y_True']).abs()
    df['Erro_Percentual'] = (df['Erro_Absoluto'] / df['Y_True']) * 100
    
    return df

# Carregar os dados
data = load_data()

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros Avançados")

# Filtros principais
modelo_selecionado = st.sidebar.multiselect(
    "Selecione Modelos:", 
    options=data['Modelo'].unique(),
    default=data['Modelo'].unique()
)

codigo_selecionado = st.sidebar.multiselect(
    "Selecione Ações:", 
    options=data['Codigo'].unique(),
    default=data['Codigo'].unique()[:3]
)

# Filtro de data
if 'Date' in data.columns:
    min_date = data['Date'].min().date()
    max_date = data['Date'].max().date()
    date_range = st.sidebar.date_input(
        "Intervalo de Datas:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

# Aplicar filtros
filtered_data = data[
    (data['Modelo'].isin(modelo_selecionado)) &
    (data['Codigo'].isin(codigo_selecionado))
]

if 'Date' in data.columns and len(date_range) == 2:
    filtered_data = filtered_data[
        (filtered_data['Date'] >= pd.Timestamp(date_range[0])) &
        (filtered_data['Date'] <= pd.Timestamp(date_range[1]))
    ]

# Layout principal
st.title("📊 Análise de Performance de Modelos Preditivos")
st.markdown("""
    **Objetivo:** Comparar o desempenho de diferentes modelos de regressão na previsão de valores de ações da B3.
""")

# Métricas gerais
st.subheader("📌 Métricas Gerais de Performance")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Número de Previsões", len(filtered_data))
with col2:
    avg_error = filtered_data['Erro_Absoluto'].mean()
    st.metric("Erro Médio Absoluto", f"{avg_error:.4f}")
with col3:
    avg_perc_error = filtered_data['Erro_Percentual'].mean()
    st.metric("Erro Percentual Médio", f"{avg_perc_error:.2f}%")
with col4:
    best_model = filtered_data.groupby('Modelo')['Erro_Absoluto'].mean().idxmin()
    st.metric("Melhor Modelo", best_model)

# Visualizações
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Comparação Modelos", 
    "📊 Análise por Ação", 
    "🧮 Simulador", 
    "🔍 Detalhes"
])

with tab1:  # Comparação de Modelos
    st.subheader("Comparação entre Modelos Preditivos")
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Previsão vs Real", "Distribuição de Erros"))
    
    # Scatter plot
    scatter = px.scatter(
        filtered_data, 
        x='Y_True', 
        y='Y_Predicted', 
        color='Modelo',
        hover_data=['Codigo', 'Date'],
        trendline="ols",
        labels={'Y_True': 'Valor Real', 'Y_Predicted': 'Valor Previsto'}
    )
    
    for trace in scatter.data:
        fig.add_trace(trace, row=1, col=1)
    
    # Linha de referência y=x
    fig.add_trace(
        go.Scatter(
            x=[filtered_data['Y_True'].min(), filtered_data['Y_True'].max()],
            y=[filtered_data['Y_True'].min(), filtered_data['Y_True'].max()],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Linha Perfeita'
        ),
        row=1, col=1
    )
    
    # Box plot de erros
    box = px.box(
        filtered_data,
        x='Modelo',
        y='Erro_Percentual',
        color='Modelo',
        labels={'Erro_Percentual': 'Erro Percentual (%)'}
    )
    
    for trace in box.data:
        fig.add_trace(trace, row=1, col=2)
    
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with tab2:  # Análise por Ação
    st.subheader("Análise Detalhada por Ação")
    
    selected_stock = st.selectbox(
        "Selecione uma Ação para Análise:",
        options=sorted(filtered_data['Codigo'].unique())
    )
    
    stock_data = filtered_data[filtered_data['Codigo'] == selected_stock]
    
    if not stock_data.empty:
        # Gráfico de evolução temporal
        fig = px.line(
            stock_data,
            x='Date',
            y=['Y_True', 'Y_Predicted'],
            color='Modelo',
            labels={'value': 'Valor', 'variable': 'Tipo'},
            title=f"Evolução Temporal - {selected_stock}",
            facet_col='Modelo',
            facet_col_wrap=2
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas por modelo para a ação selecionada
        st.subheader(f"Métricas de Performance para {selected_stock}")
        metrics = stock_data.groupby('Modelo').agg({
            'Y_True': 'mean',
            'Y_Predicted': 'mean',
            'Erro_Absoluto': 'mean',
            'Erro_Percentual': 'mean',
            'R²': 'mean'
        }).reset_index()
        
        st.dataframe(
            metrics.style.format({
                'Y_True': '{:.4f}',
                'Y_Predicted': '{:.4f}',
                'Erro_Absoluto': '{:.4f}',
                'Erro_Percentual': '{:.2f}%',
                'R²': '{:.4f}'
            }),
            use_container_width=True
        )
    else:
        st.warning("Nenhum dado disponível para a ação selecionada com os filtros atuais.")

with tab3:  # Simulador de Investimento
    st.subheader("💰 Simulador de Investimento Baseado em Modelos")
    
    capital = st.number_input(
        "Capital Inicial (R$):", 
        min_value=1000, 
        value=10000, 
        step=1000
    )
    
    available_stocks = sorted(filtered_data['Codigo'].unique())
    selected_stocks = st.multiselect(
        "Selecione as Ações para Compor a Carteira:",
        options=available_stocks,
        default=available_stocks[:3] if len(available_stocks) > 0 else []
    )
    
    if selected_stocks:
        # Calcular retornos esperados
        latest_data = filtered_data[
            filtered_data['Codigo'].isin(selected_stocks)
        ].sort_values('Date').groupby(['Codigo', 'Modelo']).last().reset_index()
        
        # Interface de alocação
        st.subheader("Alocação de Capital")
        
        allocation_method = st.radio(
            "Método de Alocação:",
            options=["Igualitária", "Baseada em Modelo", "Manual"],
            horizontal=True
        )
        
        if allocation_method == "Baseada em Modelo":
            selected_model = st.selectbox(
                "Modelo para Base da Alocação:",
                options=filtered_data['Modelo'].unique()
            )
            
            model_data = latest_data[latest_data['Modelo'] == selected_model]
            model_data['Peso'] = model_data['Y_Predicted'] / model_data['Y_Predicted'].sum()
            
            allocations = {
                row['Codigo']: row['Peso'] 
                for _, row in model_data.iterrows()
            }
            
        elif allocation_method == "Manual":
            allocations = {}
            cols = st.columns(len(selected_stocks))
            for i, stock in enumerate(selected_stocks):
                with cols[i]:
                    allocations[stock] = st.slider(
                        f"Alocação para {stock} (%)",
                        min_value=0,
                        max_value=100,
                        value=100//len(selected_stocks),
                        step=5
                    )
            
            # Normalizar para somar 100%
            total = sum(allocations.values())
            if total != 100:
                st.warning(f"A soma das alocações é {total}%. Normalizando para 100%.")
                allocations = {k: (v/total)*100 for k, v in allocations.items()}
        else:  # Igualitária
            allocations = {stock: 100/len(selected_stocks) for stock in selected_stocks}
        
        # Mostrar alocação
        allocation_df = pd.DataFrame.from_dict(allocations, orient='index', columns=['Alocação (%)']).reset_index()
        allocation_df = allocation_df.rename(columns={'index': 'Ação'})
        allocation_df['Investimento (R$)'] = allocation_df['Alocação (%)'] * capital / 100
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("### Distribuição de Alocação")
            fig = px.pie(
                allocation_df,
                names='Ação',
                values='Alocação (%)',
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("### Detalhes da Alocação")
            st.dataframe(
                allocation_df.style.format({
                    'Alocação (%)': '{:.1f}%',
                    'Investimento (R$)': 'R$ {:.2f}'
                }),
                use_container_width=True,
                hide_index=True
            )
        
        # Calcular retorno esperado
        st.subheader("Retorno Esperado")
        
        if st.button("Calcular Projeção"):
            # Obter os últimos valores previstos para cada ação
            projections = []
            for stock in selected_stocks:
                stock_proj = latest_data[
                    (latest_data['Codigo'] == stock) & 
                    (latest_data['Modelo'] == selected_model if allocation_method == "Baseada em Modelo" else True)
                ]
                if not stock_proj.empty:
                    avg_proj = stock_proj['Y_Predicted'].mean()
                    projections.append({
                        'Ação': stock,
                        'Preço Atual': stock_proj['Y_True'].iloc[0],
                        'Preço Projetado': avg_proj,
                        'Retorno Esperado (%)': ((avg_proj - stock_proj['Y_True'].iloc[0]) / stock_proj['Y_True'].iloc[0]) * 100
                    })
            
            if projections:
                projection_df = pd.DataFrame(projections)
                projection_df['Alocação (%)'] = projection_df['Ação'].map(allocations)
                projection_df['Retorno Ponderado (%)'] = projection_df['Retorno Esperado (%)'] * projection_df['Alocação (%)'] / 100
                
                total_return = projection_df['Retorno Ponderado (%)'].sum()
                final_value = capital * (1 + total_return/100)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Retorno Total Esperado", f"{total_return:.2f}%")
                with col2:
                    st.metric("Valor Final Projetado", f"R$ {final_value:,.2f}")
                
                st.write("### Detalhes por Ação")
                st.dataframe(
                    projection_df.style.format({
                        'Preço Atual': 'R$ {:.4f}',
                        'Preço Projetado': 'R$ {:.4f}',
                        'Retorno Esperado (%)': '{:.2f}%',
                        'Alocação (%)': '{:.1f}%',
                        'Retorno Ponderado (%)': '{:.2f}%'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.error("Não foi possível calcular a projeção com os dados disponíveis.")

with tab4:  # Detalhes dos Dados
    st.subheader("📋 Dados Completos")
    st.write("""
        Esta tabela contém todos os dados disponíveis após aplicação dos filtros selecionados.
        Use a caixa de busca para encontrar registros específicos.
    """)
    
    st.dataframe(
        filtered_data,
        use_container_width=True,
        column_config={
            "Date": st.column_config.DateColumn("Data"),
            "Y_True": st.column_config.NumberColumn("Valor Real", format="%.4f"),
            "Y_Predicted": st.column_config.NumberColumn("Valor Previsto", format="%.4f")
        },
        hide_index=True
    )
    
    # Opção para download
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados Filtrados (CSV)",
        data=csv,
        file_name='dados_filtrados.csv',
        mime='text/csv'
    )


#Apresentação do Dashboard
st.markdown("---")
st.header("🎯 Pontos Chave para Apresentação")

with st.expander("1. Performance Comparativa dos Modelos"):
    st.write("""
    **Decision Tree foi o modelo mais preciso**:
    - MAE: 0.012 (melhor)
    - R²: 0.997 (quase perfeito)
    
    **Lasso teve a pior performance**:
    - MAE: 0.224 
    - R²: 0.437
    """)
    fig = px.bar(
        data.groupby('Modelo')['MAE'].mean().reset_index(),
        x='Modelo', y='MAE',
        title='Erro Médio Absoluto por Modelo'
    )
    st.plotly_chart(fig)

with st.expander("2. Melhores e Piores Previsões"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Top 3 Melhores Previsões**")
        st.table(
            data.nsmallest(3, 'MAE')[['Codigo', 'Modelo', 'MAE']]
            .style.highlight_min(color='lightgreen')
        )
    with col2:
        st.write("**Top 3 Maiores Erros**")
        st.table(
            data.nlargest(3, 'MAE')[['Codigo', 'Modelo', 'MAE']]
            .style.highlight_max(color='pink')
        )

with st.expander("3. Casos de Estudo Interessantes"):
    st.write("""
    **Caso 1 - RDOR3**:
    - Modelo Linear acertou quase perfeitamente (Y_Predicted: 1.554 vs Y_True: 1.535)
    
    **Caso 2 - BRAV3**:
    - Modelo Lasso teve MAPE de 90.48%
    - Grande oportunidade para investigar causas
    """)

# Rodapé
st.markdown("---")
st.caption("Desenvolvido por Vanessa Furtado, Alexandre Tavares e Paulo Mukai - Tech_Challenge Fase 03 - FIAP - Análise de Dados da B3")

