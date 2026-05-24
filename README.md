# HIV/AIDS Dashboard

Projeto de extensao para construir um dashboard com dados publicos sobre HIV/AIDS.

Neste momento, o repositorio esta em uma base inicial. A limpeza dos dados, os indicadores e a interface do dashboard ainda serao definidos.

### Camadas

1. **Dados brutos (`data/raw/tabnet_hiv_aids`)**: Guarda os arquivos exatamente como foram baixados. Evite editar esses CSVs manualmente.
2. **Tratamento (`src/hiv_dashboard`)**: Usado para scripts de transformação de dados e caminhos importantes do projeto.
3. **Scripts (`scripts`)**: Reservada para scripts de preparo e execução de pipeline.
4. **Dashboard (`dashboard`)**: Reservada para a futura interface. Se depois a escolha for React, esta pasta pode virar `frontend/` ou conviver com uma pasta separada.

## Estrutura

```text
.
├── data/
│   ├── raw/
│   │   └── tabnet_hiv_aids/        # CSVs originais coletados
│   ├── processed/                  # Futuras bases tratadas
│   └── external/                   # GeoJSON, shapefiles e bases auxiliares
├── dashboard/                      # Futuro dashboard
├── scripts/
│   └── run_pipeline.py             # Script de execução da pipeline de dados
└── src/
    └── hiv_dashboard/
        ├── data/                   # Transformação de dados
        └── paths.py                # Caminhos principais do projeto
```

## Como rodar o placeholder

1. Instale as dependencias:

```bash
pip install -r requirements.txt
```

2. Defina a primeira rotina de leitura/limpeza dos dados.

## Proximas decisoes e passos sugeridos

- Definir como os CSVs brutos serao lidos e limpos.
- Listar quais graficos precisam existir no MVP.
- Criar a primeira rotina de preparo dos dados.
- Adicionar os graficos ao dashboard.
- Decidir se a interface final sera em Streamlit, React ou outro formato.
- Adicionar mapa usando `data/external` com GeoJSON de municipios.
