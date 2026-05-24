import sqlite3
import pandas as pd
from pathlib import Path
from src.hiv_dashboard.paths import PROCESSED_DATA_DIR, DATA_DIR

def carregar_banco_de_dados():
    db_path = DATA_DIR / 'database.sqlite'
    
    print(f"  ▸ Conectando ao banco de dados SQLite em: {db_path.name}")
    conn = sqlite3.connect(str(db_path))
    
    csv_files = sorted(PROCESSED_DATA_DIR.glob('*.csv'))
    
    if not csv_files:
        print(f"    Nenhum arquivo CSV encontrado em {PROCESSED_DATA_DIR}.")
        conn.close()
        return

    print("Iniciando a importação e normalização...")
    
    # Colunas que identificam a localidade e o ano
    colunas_contexto = ['regiao', 'uf', 'cod_ibge', 'municipio', 'ano_diagnostico']

    for csv_file in csv_files:
        file_name = csv_file.name
        table_name = csv_file.stem.lower()
        
        # remover caracteres especiais
        table_name = table_name.replace(' ', '_').replace('-', '_').replace('ç', 'c').replace('ã', 'a').replace('é', 'e')
        
        print(f"    Lendo e normalizando {file_name}...")
        
        try:
            df = pd.read_csv(csv_file)
            
            # Garantir que temos apenas as colunas de contexto que realmente existem no DF
            id_vars = [c for c in colunas_contexto if c in df.columns]
            
            # As colunas que vão ser derretidas são todas que não são contexto
            value_vars = [c for c in df.columns if c not in id_vars]
            
            # Transformar o formato Largo para Longo usando pd.melt
            df_long = pd.melt(df, id_vars=id_vars, value_vars=value_vars, 
                              var_name='categoria', value_name='quantidade')
            
            # Converter a coluna quantidade para numérico
            df_long['quantidade'] = pd.to_numeric(df_long['quantidade'], errors='coerce')
            
            # Remover linhas onde a quantidade é nula ou zero 
            df_long = df_long.dropna(subset=['quantidade'])
            df_long = df_long[df_long['quantidade'] > 0]
            
            # Salvar no SQLite
            nome_tabela_bd = f"dados_{table_name}"
            df_long.to_sql(nome_tabela_bd, conn, if_exists='replace', index=False)
            print(f"      Concluído: {len(df_long)} registros inseridos na tabela '{nome_tabela_bd}'.")
            
        except Exception as e:
            print(f"      Erro ao processar {file_name}: {e}")

    conn.close()
    print("  ▸ Processo de banco de dados finalizado!")
