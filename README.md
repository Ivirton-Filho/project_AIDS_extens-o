# HIV/AIDS Dashboard

Projeto de extensao para construir um dashboard com dados publicos sobre HIV/AIDS.

Neste momento, o repositorio esta em uma base inicial. A limpeza dos dados, os indicadores e a interface do dashboard ainda serao definidos.

## Estrutura

```text
.
├── data/
│   ├── raw/
│   │   └── tabnet_hiv_aids/        # CSVs originais coletados
│   ├── processed/                  # Futuras bases tratadas
│   └── external/                   # GeoJSON, shapefiles e bases auxiliares
├── dashboard/                      # Futuro dashboard
├── docs/
│   └── arquitetura.md              # Decisoes e proximos passos
└── src/
    └── hiv_dashboard/
        └── paths.py                # Caminhos principais do projeto
```

## Como rodar o placeholder

1. Instale as dependencias:

```bash
pip install -r requirements.txt
```

2. Defina a primeira rotina de leitura/limpeza dos dados.

## Proximas decisoes

- definir como os CSVs brutos serao lidos;
- definir a estrategia de limpeza;
- definir quais graficos entram no MVP;
- decidir se a interface final sera em Streamlit, React ou outro formato;
- adicionar mapas somente depois de escolher a base geografica.
