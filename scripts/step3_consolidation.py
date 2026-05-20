import re
from pathlib import Path

import pandas as pd

from step1_reading import ler_csv_tabnet
from step2_cleaning import limpar_dataframe

# Caminhos
PASTA_BRUTOS = Path(__file__).resolve().parents[1] / "data" / "raw" / "tabnet_hiv_aids"
PASTA_SAIDA = Path(__file__).resolve().parents[1] / "data" / "processed"


def extrair_info_caminho(caminho: Path) -> dict:
    """
    Extrai regiao, uf, ano e dimensao a partir do caminho do arquivo.

    Exemplo: .../tabnet_hiv_aids/NORDESTE/PE/2023/SEXO.csv
    Retorna: {"regiao": "NORDESTE", "uf": "PE", "ano": 2023, "dimensao": "SEXO"}
    """
    partes = caminho.parts
    idx = list(partes).index("tabnet_hiv_aids")

    regiao = partes[idx + 1]
    uf = partes[idx + 2]
    pasta_ano = partes[idx + 3]
    dimensao = caminho.stem

    # Extrair so o numero do ano (ignorar texto como "Ate setembro")
    ano = int(re.match(r"(\d{4})", pasta_ano).group(1))

    # Normalizar nome da dimensao (RACA-COR e RACA_COR viram a mesma coisa)
    dimensao = dimensao.upper().replace("-", "_")

    return {"regiao": regiao, "uf": uf, "ano": ano, "dimensao": dimensao}


def adicionar_nao_informado(df_dimensao: pd.DataFrame, df_ano: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a coluna "nao_informado" comparando com o total do ANO.
    """
    df = df_dimensao.copy()

    # Pegar o total de casos por municipio do ANO.csv
    colunas_ano = [c for c in df_ano.columns if c not in ("cod_ibge", "municipio")]
    df_ano_copy = df_ano.copy()
    df_ano_copy["total_ano"] = df_ano_copy[colunas_ano].sum(axis=1)

    # Criar dicionario: municipio -> total de casos
    totais = dict(zip(df_ano_copy["municipio"], df_ano_copy["total_ano"]))

    # Calcular soma das categorias da dimensao
    colunas_dados = [c for c in df.columns if c not in ("cod_ibge", "municipio")]
    df["soma_categorias"] = df[colunas_dados].sum(axis=1)

    # nao_informado = total do ano - soma das categorias
    df["nao_informado"] = df["municipio"].map(totais).fillna(0).astype(int) - df["soma_categorias"]
    df["nao_informado"] = df["nao_informado"].clip(lower=0)

    df = df.drop(columns=["soma_categorias"])

    return df


def consolidar():
    """
    Percorre todos os CSVs, limpa e salva os 5 arquivos finais.
    """
    print("=" * 50)
    print("ETAPA 3 - CONSOLIDACAO DOS DADOS")
    print("=" * 50)

    # Listar todos os CSVs
    csvs = sorted(PASTA_BRUTOS.rglob("*.csv"))
    print(f"Encontrados {len(csvs)} CSVs\n")

    # Primeiro: ler todos os ANO.csv para ter os totais de referencia
    # Chave: (uf, ano) -> DataFrame limpo do ANO
    totais_por_uf_ano = {}

    # Acumular DataFrames por dimensao
    dados_por_dimensao = {}

    erros = 0

    for caminho in csvs:
        try:
            info = extrair_info_caminho(caminho)
            df_bruto = ler_csv_tabnet(caminho)
            df_limpo = limpar_dataframe(df_bruto)

            # Adicionar colunas de contexto
            df_limpo["regiao"] = info["regiao"]
            df_limpo["uf"] = info["uf"]
            df_limpo["ano_diagnostico"] = info["ano"]

            # Reordenar: contexto primeiro
            colunas_contexto = ["regiao", "uf", "cod_ibge", "municipio", "ano_diagnostico"]
            colunas_dados = [c for c in df_limpo.columns if c not in colunas_contexto]
            df_limpo = df_limpo[colunas_contexto + colunas_dados]

            dimensao = info["dimensao"]

            # Guardar os ANO para referencia
            if dimensao == "ANO":
                totais_por_uf_ano[(info["uf"], info["ano"])] = df_limpo.copy()

            # Acumular por dimensao
            if dimensao not in dados_por_dimensao:
                dados_por_dimensao[dimensao] = []
            dados_por_dimensao[dimensao].append(df_limpo)

        except Exception as e:
            erros += 1
            print(f"  ERRO em {caminho.name}: {e}")

    print(f"Processados: {len(csvs) - erros} CSVs ({erros} erros)\n")

    # Juntar e salvar cada dimensao
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    # Nomes dos arquivos de saida
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

        # Adicionar nao_informado (exceto para ANO, que ja tem o total)
        if dimensao != "ANO":
            partes = []
            for (uf, ano), grupo in df_final.groupby(["uf", "ano_diagnostico"]):
                chave = (uf, ano)
                if chave in totais_por_uf_ano:
                    df_ref = totais_por_uf_ano[chave]
                    # Remover colunas de contexto do df_ref para o calculo
                    df_ref_limpo = df_ref[["cod_ibge", "municipio"] + [
                        c for c in df_ref.columns
                        if c not in ("regiao", "uf", "cod_ibge", "municipio", "ano_diagnostico")
                    ]]
                    grupo_com_ni = adicionar_nao_informado(
                        grupo.drop(columns=["regiao", "uf", "ano_diagnostico"]),
                        df_ref_limpo,
                    )
                    # Readicionar contexto
                    grupo_com_ni["regiao"] = grupo["regiao"].iloc[0]
                    grupo_com_ni["uf"] = uf
                    grupo_com_ni["ano_diagnostico"] = ano
                    colunas_contexto = ["regiao", "uf", "cod_ibge", "municipio", "ano_diagnostico"]
                    colunas_resto = [c for c in grupo_com_ni.columns if c not in colunas_contexto]
                    grupo_com_ni = grupo_com_ni[colunas_contexto + colunas_resto]
                    partes.append(grupo_com_ni)
                else:
                    partes.append(grupo)
            df_final = pd.concat(partes, ignore_index=True)

        # Salvar
        nome = nomes_saida.get(dimensao, dimensao.lower())
        df_final.to_csv(PASTA_SAIDA / f"{nome}.csv", index=False, encoding="utf-8-sig")
        print(f"  {nome}.csv: {len(df_final):,} registros")

    print("\nConsolidacao concluida!")


if __name__ == "__main__":
    consolidar()
