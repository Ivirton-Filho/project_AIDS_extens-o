"""
Etapa 1 - Ler um CSV bruto do TabNet corretamente.

Problema: os CSVs do TabNet tem ~8 linhas de metadados antes dos dados reais.
Alem disso, usam encoding latin-1 e separador ";".

Este script resolve esses 3 problemas.
"""

from io import StringIO
from pathlib import Path

import pandas as pd

# Caminho de um CSV de exemplo para testar
CAMINHO_EXEMPLO = (
    Path(__file__).resolve().parents[1]
    / "data" / "raw" / "tabnet_hiv_aids"
    / "NORDESTE" / "PE" / "2023" / "SEXO.csv"
)


def ler_csv_tabnet(caminho: Path) -> pd.DataFrame:
    """
    Le um CSV exportado do TabNet/DATASUS.

    Os CSVs do TabNet vem assim:
        Casos de aids identificados no Brasil       <- metadado (pular)
        Frequencia por Municipio (Res) e Sexo       <- metadado (pular)
        Ano Diagnostico: 2023                       <- metadado (pular)
        ...mais metadados...                        <- metadado (pular)
        "Municipio (Res)";"Masculino";"Feminino"    <- header real (AQUI!)
        "260005 Abreu e Lima";22;5;27               <- dados
        "260160 Recife";414;178;592                  <- dados

    Estrategia:
        1. Ler o arquivo inteiro como texto com encoding latin-1
        2. Encontrar a linha do header real (primeira que comeca com aspas e tem ";")
        3. Passar so essa parte pro pandas
    """
    # 1. Ler o arquivo com encoding correto
    conteudo = caminho.read_text(encoding="latin-1")
    linhas = conteudo.splitlines()

    # 2. Encontrar onde comeca o header real
    linha_header = 0
    for i, linha in enumerate(linhas):
        if linha.strip().startswith('"') and ";" in linha:
            linha_header = i
            break

    # 3. Pegar so a parte dos dados (do header pra baixo)
    texto_dados = "\n".join(linhas[linha_header:])

    # 4. Ler como DataFrame
    df = pd.read_csv(
        StringIO(texto_dados),
        sep=";",
        quotechar='"',
        dtype=str,  # Ler tudo como texto por enquanto
    )

    return df


# --- Teste ---
if __name__ == "__main__":
    print(f"Lendo: {CAMINHO_EXEMPLO.name}")
    print(f"Caminho: {CAMINHO_EXEMPLO}\n")

    df = ler_csv_tabnet(CAMINHO_EXEMPLO)

    print(f"Linhas: {len(df)}")
    print(f"Colunas: {list(df.columns)}\n")
    print(df.head(5).to_string(index=False))
    print(f"\n...ultimas 3 linhas:")
    print(df.tail(3).to_string(index=False))
