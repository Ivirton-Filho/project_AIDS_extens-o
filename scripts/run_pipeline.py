import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.hiv_dashboard.paths import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.hiv_dashboard.data.step1_reading import ler_csv_tabnet
from src.hiv_dashboard.data.step2_cleaning import limpar_dataframe
from src.hiv_dashboard.data.step3_transform import consolidar
from src.hiv_dashboard.data.step4_load_db import carregar_banco_de_dados

def verificar_dados_brutos():
    print(f"\n{'=' * 50}")
    print("VERIFICAÇÃO DOS DADOS BRUTOS")
    print(f"{'=' * 50}")

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Pasta de dados brutos não encontrada"
        )

    csvs = sorted(RAW_DATA_DIR.rglob("*.csv"))
    if not csvs:
        raise FileNotFoundError(
            f"Nenhum CSV encontrado"
        )

    print(f"\n  Pasta: {RAW_DATA_DIR}")
    return csvs

def executar_consolidacao():
    #Executa step1, step2 e step3.
    print(f"\n{'=' * 50}")
    print("LEITURA, LIMPEZA E TRANSFORMAÇÃO")
    print(f"{'=' * 50}")

    # Listar CSVs brutos
    csvs = sorted(RAW_DATA_DIR.rglob("*.csv"))
    print(f"\n  Encontrados {len(csvs)} CSVs\n")

    # Step 1 + 2:
    dados_lidos = []
    erros = 0

    print("  ▸ Leitura e limpeza...")
    for caminho in csvs:
        try:
            df_bruto = ler_csv_tabnet(caminho)
            df_limpo = limpar_dataframe(df_bruto)
            dados_lidos.append((caminho, df_limpo))
        except Exception as e:
            print(f"    ERRO em {caminho.name}: {e}")

    print(f"    {len(dados_lidos)} processados\n")

    # Step 3:
    print("  ▸ Consolidação e salvamento...")
    consolidar(dados_lidos)

def main():
    print( "═" * 50 )
    print(" PIPELINE DE DADOS — HIV/AIDS ".center(50))
    print( "═" * 50 )

    sucesso = True

    # --- Etapa 1: Verificação ---
    try:
        verificar_dados_brutos()
    except Exception as e:
        print(f"\n FALHA: {e}")
        sys.exit(1)

    # --- Etapa 2: Consolidação ---
    try:
        executar_consolidacao()
    except Exception as e:
        print(f"\n FALHA na consolidação: {e}")
        sucesso = False

    # --- Etapa 3: Carga no Banco de Dados ---
    if sucesso:
        try:
            print(f"\n{'=' * 50}")
            print("CARGA NO BANCO DE DADOS")
            print(f"{'=' * 50}\n")
            carregar_banco_de_dados()
        except Exception as e:
            print(f"\n FALHA na carga do banco: {e}")
            sucesso = False

    # --- Resumo final ---
    print(f"\n{'=' * 52}")
    if sucesso:
        print(f"  ✔ Pipeline concluído com sucesso")
    else:
        print(f"  ✘ Pipeline concluído com erros")
    print(f"{'=' * 52}\n")

if __name__ == "__main__":
    main()
