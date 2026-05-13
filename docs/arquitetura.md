# Arquitetura do projeto

## Decisao principal

A interface e a preparacao de dados devem ficar separadas. Isso permite tres caminhos:

- criar o dashboard em Streamlit;
- criar uma API em Python depois;
- criar uma interface em React consumindo os CSVs tratados ou uma API.

Neste primeiro commit, o repositorio fica apenas com a estrutura base. A limpeza dos dados ainda nao foi definida.

## Camadas

### 1. Dados brutos

Pasta: `data/raw/tabnet_hiv_aids`

Guarda os arquivos exatamente como foram baixados. Evite editar esses CSVs manualmente.

### 2. Tratamento

Pasta: `src/hiv_dashboard`

Por enquanto, contem apenas `paths.py`, usado para centralizar caminhos importantes do projeto.

### 3. Scripts

Pasta: `scripts`

Reservada para futuros scripts de preparo, validacao ou analise exploratoria.

### 4. Dashboard

Pasta: `dashboard`

Reservada para a futura interface. Se depois a escolha for React, esta pasta pode virar `frontend/` ou conviver com uma pasta separada.

## Proximos passos sugeridos

1. Escolher o recorte da apresentacao: Brasil, regiao, UF ou municipio.
2. Definir como os CSVs brutos serao lidos e limpos.
3. Listar quais graficos precisam existir no MVP.
4. Criar a primeira rotina de preparo dos dados.
5. Adicionar os graficos ao dashboard.
6. Adicionar mapa usando `data/external` com GeoJSON de municipios.
