from io import StringIO
from pathlib import Path

import pandas as pd


def ler_csv_tabnet(caminho: Path) -> pd.DataFrame:
    """
    Lê um arquivo CSV do TabNet ignorando cabeçalhos sujos e forçando todos
    os dados a serem lidos como texto para posterior tratamento.
    """
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
