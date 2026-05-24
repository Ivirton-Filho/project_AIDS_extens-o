import re
from pathlib import Path
import pandas as pd

from src.hiv_dashboard.paths import PROCESSED_DATA_DIR

COLUNAS_CONTEXTO = ["regiao", "uf", "cod_ibge", "municipio", "ano_diagnostico"]

def extrair_info_caminho(caminho: Path) -> dict:

    partes = caminho.parts
    idx = list(partes).index("tabnet_hiv_aids")

    regiao = partes[idx + 1]
    uf = partes[idx + 2]
    pasta_ano = partes[idx + 3]
    dimensao = caminho.stem

    # Extrair so o numero do ano (procura em qualquer lugar do nome da pasta)
    match_ano = re.search(r"(\d{4})", pasta_ano)
    if not match_ano:
        raise ValueError(f"Não foi possível encontrar um ano na pasta '{pasta_ano}' (caminho: {caminho})")
    ano = int(match_ano.group(1))

    dimensao = dimensao.upper().replace("-", "_")

    return {"regiao": regiao, "uf": uf, "ano": ano, "dimensao": dimensao}


def adicionar_nao_informado(df_dimensao: pd.DataFrame, df_ano: pd.DataFrame) -> pd.DataFrame:
    # Calcula a coluna "nao_informado" comparando com o total do ANO.
    df = df_dimensao.copy()

    # Calcular o total do ano por municipio
    colunas_ano = [c for c in df_ano.columns if c not in COLUNAS_CONTEXTO]
    totais = dict(zip(df_ano["municipio"], df_ano[colunas_ano].sum(axis=1)))

    # Calcular soma das categorias da dimensao
    colunas_dados = [c for c in df.columns if c not in COLUNAS_CONTEXTO]
    df["soma_categorias"] = df[colunas_dados].sum(axis=1)

    # nao_informado = total do ano - soma das categorias
    df["nao_informado"] = df["municipio"].map(totais).fillna(0).astype(int) - df["soma_categorias"]
    df["nao_informado"] = df["nao_informado"].clip(lower=0)

    return df.drop(columns=["soma_categorias"])

def consolidar(dados_lidos: list):

    PASTA_SAIDA = PROCESSED_DATA_DIR

    # Chave: (uf, ano) -> DataFrame limpo do ANO
    totais_por_uf_ano = {}

    # Acumular DataFrames por dimensao
    dados_por_dimensao = {}

    for caminho, df_limpo in dados_lidos:
        info = extrair_info_caminho(caminho)

        # Adicionar colunas de contexto
        df_limpo["regiao"] = info["regiao"]
        df_limpo["uf"] = info["uf"]
        df_limpo["ano_diagnostico"] = info["ano"]

        # Reordenar: contexto primeiro
        colunas_dados = [c for c in df_limpo.columns if c not in COLUNAS_CONTEXTO]
        df_limpo = df_limpo[COLUNAS_CONTEXTO + colunas_dados]

        dimensao = info["dimensao"]

        # Guardar os ANO para referencia
        if dimensao == "ANO":
            totais_por_uf_ano[(info["uf"], info["ano"])] = df_limpo.copy()

        # Acumular por dimensao
        if dimensao not in dados_por_dimensao:
            dados_por_dimensao[dimensao] = []
        dados_por_dimensao[dimensao].append(df_limpo)

    # Juntar e salvar cada dimensao
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    nomes_saida = {
        "ANO": "ano",
        "SEXO": "sexo",
        "IDADE": "idade",
        "ESCOLARIDADE": "escolaridade",
        "RACA_COR": "raca_cor",
    }

    print("Salvando em data/processed/:\n")

    for dimensao, lista_dfs in dados_por_dimensao.items():
        df_final = pd.concat(lista_dfs, ignore_index=True)

        # Adicionar nao_informado
        if dimensao != "ANO":
            partes = []
            for (uf, ano), grupo in df_final.groupby(["uf", "ano_diagnostico"]):
                chave = (uf, ano)
                if chave in totais_por_uf_ano:
                    grupo_com_ni = adicionar_nao_informado(grupo, totais_por_uf_ano[chave])
                    partes.append(grupo_com_ni)
                else:
                    partes.append(grupo)
            df_final = pd.concat(partes, ignore_index=True)

        # Salvar
        nome = nomes_saida.get(dimensao, dimensao.lower())
        df_final.to_csv(PASTA_SAIDA / f"{nome}.csv", index=False, encoding="utf-8-sig")

    print("\nConsolidacao concluida!")
