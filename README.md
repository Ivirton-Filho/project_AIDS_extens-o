# HIV/AIDS Dashboard

Projeto de extensão para construir um dashboard interativo com dados públicos sobre HIV/AIDS extraídos do TabNet (DATASUS).

O projeto é composto por uma **Pipeline de Dados** automatizada — que extrai, limpa, transforma e consolida os dados brutos em um banco de dados SQLite —, e um **Dashboard Epidemiológico** construído com Streamlit para a visualização dinâmica dos indicadores.

## Arquitetura e Estrutura do Projeto

```text
.
├── data/
│   ├── raw/
│   │   └── tabnet_hiv_aids/        # CSVs originais coletados do TabNet (Não versionados)
│   ├── processed/                  # Arquivos intermediários e processados
│   └── database.sqlite             # Banco de dados SQLite gerado (Não versionado)
├── dashboard/
│   └── dashboard.py                # Aplicação principal do Dashboard em Streamlit
├── scripts/
│   └── run_pipeline.py             # Script orquestrador que executa a pipeline de ETL
├── src/
│   ├── __init__.py                 # Arquivo de inicialização do pacote
│   ├── step1_reading.py            # Módulo de leitura
│   ├── step2_cleaning.py           # Módulo de limpeza
│   ├── step3_transform.py          # Módulo de transformação
│   ├── step4_load_db.py            # Módulo de carga
│   └── paths.py                    # Gerenciamento dinâmico de caminhos das pastas
├── requirements.txt                # Dependências Python do projeto
└── README.md                       # Documentação do projeto
```

## Passo a Passo para Rodar o Projeto

Siga as etapas abaixo para configurar o ambiente, processar os dados de forma local e iniciar a visualização no seu navegador.

### 1. Preparar o Ambiente

Certifique-se de ter o [Python](https://www.python.org/) instalado. Recomendamos a utilização de um ambiente virtual (ex: `venv` ou `conda`) para isolar as dependências.

Com o ambiente ativado, instale as bibliotecas necessárias rodando na raiz do projeto:

```bash
pip install -r requirements.txt
```

### 2. Inserir os Dados Brutos

O repositório está configurado para ignorar os arquivos de banco de dados e dados brutos devido ao seu tamanho. Portanto, você deve garantir que os arquivos `.csv` do TabNet estejam disponíveis localmente no caminho correto:
**`data/raw/tabnet_hiv_aids/`**

### 3. Executar a Pipeline de Dados

Com os dados na pasta correta, execute a pipeline. Este processo fará a limpeza, o agrupamento das categorias e criará o arquivo `data/database.sqlite`.

Na raiz do repositório, rode o script:

```bash
python scripts/run_pipeline.py
```

*Verifique se o terminal retorna a mensagem: `✔ Pipeline concluído com sucesso`.*

### 4. Iniciar o Dashboard

Após a consolidação dos dados no banco SQLite, inicie a interface gráfica rodando a aplicação Streamlit:

```bash
streamlit run dashboard/dashboard.py
```

O comando abrirá uma nova aba automaticamente no seu navegador (geralmente em `http://localhost:8501`).

---

**Funcionalidades Atuais do Dashboard:**
- Filtros dinâmicos em cascata por Região, Estado (UF) e Município.
- Totalizadores (Métricas) gerais e divididos por sexo.
- Gráficos interativos contemplando evolução por Ano, Sexo, Raça/Cor, Faixa Etária e Escolaridade.
- Mapa Coroplético de casos por Estado no Brasil (quando "Todas" as UFs estão selecionadas) e Gráfico de Barras comparativo por Municípios ao filtrar uma UF específica.
