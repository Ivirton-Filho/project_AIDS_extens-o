import geopandas as gpd
import pandas as pd

shape = gpd.read_file("data/external/BR_Municipios_2025/BR_Municipios_2025.shp")

dados = pd.read_csv("data/processed/ano.csv")

# Separar registros sem codigo IBGE, como "Ignorado"
dados_ignorados = dados[dados["cod_ibge"].isna()].copy()
dados_mapa = dados[dados["cod_ibge"].notna()].copy()

# Garantir que o codigo IBGE do shapefile fique como string com 7 digitos
shape["cod_ibge"] = (
    pd.to_numeric(shape["CD_MUN"], errors="coerce")
    .astype("float")
    .astype("Int64")
    .astype(str)
    .str.zfill(7)
)

# Garantir que o codigo IBGE do banco fique como string com 7 digitos
dados_mapa["cod_ibge"] = (
    pd.to_numeric(dados_mapa["cod_ibge"], errors="coerce")
    .astype("float")
    .astype("Int64")
    .astype(str)
    .str.zfill(7)
)

# Fazer o merge usando cod_ibge como chave
mapa_dados = shape.merge(dados_mapa, on="cod_ibge", how="left")

print(mapa_dados.head())
print(mapa_dados[["cod_ibge", "NM_MUN", "municipio"]].head())
print(mapa_dados.columns)
print(f"Registros sem codigo IBGE separados: {len(dados_ignorados)}")