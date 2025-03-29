import pandas as pd
import glob
import unidecode
import os

def load_and_normalize_data(file_path_pattern):
    """Carrega e normaliza os dados de múltiplos arquivos CSV."""
    all_files = glob.glob(file_path_pattern)
    print(f"Arquivos encontrados: {all_files}")
    df_list = []
    processed_files = []  # Lista para armazenar os arquivos processados
    
    for file in all_files:
        try:
            print(f"Lendo arquivo: {file}")
            # Ler o arquivo com o delimitador correto e forçar a leitura da coluna 'date' como texto
            df = pd.read_csv(file, delimiter=';', dtype={'date': str}, quotechar='"')
            
            # Verificar se os cabeçalhos estão corretos
            expected_headers = ['date', 'setor', 'codigo', 'acao', 'tipo', 'qtde_teorica', 'part_percent', 'part_acum_percent']
            if not all(header in df.columns for header in expected_headers):
                print(f"Erro: Cabeçalhos incorretos ou faltando no arquivo {file}")
                continue

            # Converter a coluna 'date' para o formato datetime
            df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d", errors="coerce")
            
            # Preencher valores ausentes na coluna 'date' com o valor da linha anterior
            df['date'] = df['date'].fillna(method='ffill')
            
            # Preencher valores ausentes na coluna 'setor' com o valor da linha anterior
            df['setor'] = df['setor'].fillna(method='ffill')
            
            # Normalizar setores
            df['setor'] = df['setor'].apply(lambda x: unidecode.unidecode(x).title() if isinstance(x, str) else x)
            df['setor'] = df['setor'].str.replace(r'[^a-zA-Z0-9 /]', '', regex=True)

            df_list.append(df)
            processed_files.append(file)
        except Exception as e:
            print(f"Erro ao processar o arquivo {file}: {e}")
    
    if df_list:
        consolidated_data = pd.concat(df_list, ignore_index=True)
        
        # Preencher valores ausentes na coluna 'date' após a consolidação
        consolidated_data['date'] = consolidated_data['date'].fillna(method='ffill')
        
        # Preencher valores ausentes na coluna 'setor' após a consolidação
        consolidated_data['setor'] = consolidated_data['setor'].fillna(method='ffill')
        
        # Exibir valores únicos das colunas para depuração
        print(f"Datas únicas após a consolidação: {consolidated_data['date'].unique()}")
        print(f"Setores únicos após a consolidação: {consolidated_data['setor'].unique()}")
        
        print(f"Dados consolidados. Total de linhas: {consolidated_data.shape[0]}")
        print(f"Arquivos processados: {processed_files}")
    else:
        consolidated_data = pd.DataFrame()
        print("Nenhum arquivo foi processado.")
    
    return consolidated_data


def save_incremental_data(data, output_file):
    """Salva os dados consolidados no arquivo especificado."""
    if not data.empty:
        try:
            if os.path.exists(output_file):
                data.to_csv(output_file, mode='a', header=False, index=False, sep=';')
            else:
                data.to_csv(output_file, index=False, sep=';')
            print(f"Dados salvos em: {output_file}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo {output_file}: {e}")


def main():
    input_path_pattern = '../01_elt_etl/bovespa/*.csv'
    output_file = 'consolidated_data.csv'
    
    data = load_and_normalize_data(input_path_pattern)
    if not data.empty:
        print("Amostra dos dados consolidados:")
        print(data.head())
    
    save_incremental_data(data, output_file)


if __name__ == '__main__':
    main()