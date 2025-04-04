import pandas as pd
import numpy as np
import glob
import unidecode

def load_data(file_path_pattern):
    all_files = glob.glob(file_path_pattern)
    df_list = []
    for file in all_files:
        df = pd.read_csv(file, delimiter=';')
        df_list.append(df)
    return pd.concat(df_list, ignore_index=True)

def normalize_sectors(data):
    # Remover acentos e converter para case uniforme
    data['setor'] = data['setor'].apply(lambda x: unidecode.unidecode(x).title() if isinstance(x, str) else x)
    
    # Mapeamento para unificar nomes similares
    sector_mapping = {
        'Bens Indls': 'Bens Industriais',
        'Cons N Basico': 'Consumo Não Básico',
        'Cons N Ciclico': 'Consumo Não Cíclico',
        'Financ E Outros': 'Financeiro e Outros',
        'Mats Basicos': 'Materiais Básicos',
        'Petroleo/ Gas E Biocombustiveis': 'Petróleo e Gás',
        'Saude/Comercio Distr': 'Saúde',
        'Tec.Informacao': 'Tecnologia da Informação',
        'Utilidade Publ': 'Utilidades Públicas'
    }
    
    # Aplicar o mapeamento para normalizar os setores
    data['setor'] = data['setor'].replace(sector_mapping, regex=True)
    return data

def preprocess_data(data):
    data = normalize_sectors(data)
    # Gerar dummies após a limpeza
    data = pd.get_dummies(data, columns=['setor', 'codigo', 'acao', 'tipo'])
    return data

def main():
    data = load_data('../01_elt_etl/bovespa/*.csv')
    data = preprocess_data(data)
    if data.empty:
        raise ValueError("Não há dados válidos para processar após a pré-processamento.")
    # Salvar dados limpos para verificação
    data.to_csv('cleaned_data.csv', index=False)
    print("Dados foram limpos e salvos com sucesso.")

if __name__ == '__main__':
    main()
