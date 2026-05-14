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
    # Ler o arquivo com encoding correto
    conteudo = caminho.read_text(encoding="latin-1")
    linhas = conteudo.splitlines()

    # Encontrar onde comeca o header real
    linha_header = 0
    for i, linha in enumerate(linhas):
        if linha.strip().startswith('"') and ";" in linha:
            linha_header = i
            break

    # Pegar so a parte dos dados (do header pra baixo)
    texto_dados = "\n".join(linhas[linha_header:])

    df = pd.read_csv(
        StringIO(texto_dados),
        sep=";",
        quotechar='"',
        dtype=str, 
    )

    return df

if __name__ == "__main__":
    print(f"Lendo: {CAMINHO_EXEMPLO.name}")
    print(f"Caminho: {CAMINHO_EXEMPLO}\n")

    df = ler_csv_tabnet(CAMINHO_EXEMPLO)

    print(f"Linhas: {len(df)}")
    print(f"Colunas: {list(df.columns)}\n")
    print(df.head(5).to_string(index=False))
    print(f"\n...ultimas 3 linhas:")
    print(df.tail(3).to_string(index=False))
