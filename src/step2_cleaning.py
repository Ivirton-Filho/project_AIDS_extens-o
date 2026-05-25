import re
import pandas as pd

def limpar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa o dataframe bruto extraído do TabNet.
    Separa códigos do IBGE dos nomes de municípios e remove lixo.
    """
    df = df.copy()

    #Separar codigo IBGE e nome do municipio 
    coluna_municipio = df.columns[0]

    codigos = []
    nomes = []
    for valor in df[coluna_municipio]:
        valor = str(valor).strip()

        if valor.lower() == "total":
            codigos.append(None)
            nomes.append("Total")
        elif "ignorado" in valor.lower():
            codigos.append(None)
            nomes.append("Ignorado")
        else:
            match = re.match(r"^(\d+)\s+(.+)$", valor)
            if match:
                codigos.append(int(match.group(1)))
                nomes.append(match.group(2).strip())
            else:
                codigos.append(None)
                nomes.append(valor)

    df["cod_ibge"] = codigos
    df["municipio"] = nomes
    df = df.drop(columns=[coluna_municipio])

    # Remover linha de "Total"
    df = df[df["municipio"] != "Total"].copy()

    # Remover coluna "Total"
    if "Total" in df.columns:
        df = df.drop(columns=["Total"])

    # Converter colunas de dados para inteiros
    colunas_de_dados = [
        c for c in df.columns if c not in ("cod_ibge", "municipio")
    ]
    for col in colunas_de_dados:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Reordenar: cod_ibge e municipio primeiro
    df = df[["cod_ibge", "municipio"] + colunas_de_dados]

    return df
