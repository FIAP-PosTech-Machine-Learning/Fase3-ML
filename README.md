
## Funcionalidades
1. **Web Scraping**:
   - Baixa os dados financeiros mais recentes da B3.
   - Armazena os dados localmente no diretório `data_pipeline/bovespa`.

2. **Upload para AWS S3**:
   - Envia os arquivos CSV para um bucket S3 configurado no arquivo `config.ini`.

3. **Análise de Dados e Machine Learning**:
   - Realiza experimentos de regressão usando modelos como:
     - Regressão Linear
     - Ridge
     - Lasso
     - Decision Tree
     - XGBoost
   - Avalia os modelos com métricas como MSE, R², MAE e MAPE.

4. **Dashboard Interativo**:
   - Visualiza os resultados das análises e predições em um dashboard interativo criado com Streamlit.

## Configuração
1. **Pré-requisitos**:
   - Python 3.8 ou superior
   - Instalar as dependências listadas no arquivo `requirements.txt`:
     ```bash
     pip install -r requirements.txt
     ```

2. **Configuração do `config.ini`**:
   - Atualize o arquivo `config.ini` com suas credenciais da AWS e a URL da B3.

3. **Configuração do WebDriver**:
   - Certifique-se de que o ChromeDriver está instalado e configurado no PATH do sistema.

## Como Executar
1. **Baixar e Enviar Dados para o S3**:
   - Execute o script `app.py`:
     ```bash
     python app.py
     ```

2. **Treinar Modelos de Regressão**:
   - Abra o notebook `machine_learning/regression_notebook.ipynb` no Jupyter Notebook ou no Visual Studio Code e execute as células.

3. **Visualizar Resultados no Dashboard**:
   - Execute o script `dashboard.py` para iniciar o dashboard interativo:
     ```bash
     streamlit run dashboard.py
     ```
   - O Streamlit abrirá automaticamente o dashboard no navegador padrão. Caso não abra, acesse o endereço exibido no terminal, geralmente `http://localhost:8501`.

4. **Visualizar Resultados**:
   - Os resultados das predições estão disponíveis no arquivo [model_results.csv](http://_vscodecontentref_/4).

## Dependências
As dependências do projeto estão listadas no arquivo `requirements.txt`. Aqui estão as principais bibliotecas utilizadas:
- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `scikit-learn`
- `xgboost`
- `boto3`
- `selenium`
- `configparser`
- `streamlit`

## Contribuição
