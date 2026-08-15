# ⚓ LH Nautical — Data Challenge

Projeto desenvolvido para o desafio técnico da **LH Nautical**, cobrindo etapas de exploração, engenharia e análise de dados, previsão de demanda e sistema de recomendação.

O objetivo foi trabalhar os dados de ponta a ponta: partir dos arquivos CSV fornecidos pelo ERP, estruturar e carregar os dados, responder às questões de negócio e consolidar os principais resultados em um dashboard interativo.

---

## 📌 Visão Geral

O projeto percorre diferentes etapas de uma jornada de dados:

* Análise exploratória dos dados;
* Geração automática de schema PostgreSQL;
* Carregamento dos arquivos CSV;
* Análise de clientes;
* Construção de dimensão calendário;
* Previsão de demanda;
* Sistema de recomendação;
* Dashboard analítico.

---

## 🗂️ Estrutura do Projeto

```text
lh-nautical-data-challenge/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── outputs/
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_schema_generation.ipynb
│   ├── 03_customer_analysis.ipynb
│   ├── 04_calendar_dimension.ipynb
│   ├── 05_demand_forecasting.ipynb
│   └── 06_recommendation_system.ipynb
│
├── src/
│   └── data/
│       ├── generate_schema.py
│       └── load_csvs.py
│
├── sql/
│   └── schema.sql
│
├── dashboard/
│   ├── app.py
│   ├── pages/
│   │   ├── overview.py
│   │   ├── customers.py
│   │   └── models.py
│   └── utils/
│       └── data_loader.py
│
├── .streamlit/
│   └── config.toml
│
├── requirements.txt
└── README.md
```

---

## 🛠️ Tecnologias Utilizadas

<div align="left">

* **Python 3**
* **SQL**
* **DuckDB**
* **PostgreSQL**
* **Pandas**
* **NumPy**
* **Streamlit**
* **Plotly**

</div>

Na etapa de geração automática do schema, foram utilizadas exclusivamente bibliotecas padrão do Python, conforme exigido pelo desafio.

---

# 📊 Etapas do Desafio

## 1. Análise Exploratória

Foi realizada uma análise inicial da tabela `orders`, observando:

* Quantidade de registros;
* Período disponível;
* Valores mínimo, máximo e médio de `total`;
* Valores nulos;
* Potenciais outliers;
* Consistência inicial da tabela.

### Resultado geral

| Métrica      |    Resultado |
| ------------ | -----------: |
| Pedidos      |       48.998 |
| Ticket médio | R$ 28.704,99 |
| Período      |  2020 a 2026 |

---

## 2. Geração Automática de Schema

Foi desenvolvido um script em Python responsável por:

1. Percorrer automaticamente todos os arquivos CSV;
2. Identificar os cabeçalhos;
3. Inferir os tipos das colunas;
4. Converter os tipos para PostgreSQL;
5. Criar uma instrução `CREATE TABLE` por arquivo;
6. Consolidar o resultado em um único `schema.sql`.

O processo identificou:

```text
24 arquivos CSV
24 tabelas geradas
```

Arquivo principal:

```text
src/data/generate_schema.py
```

Arquivo gerado:

```text
sql/schema.sql
```

---

## 3. Carregamento dos Dados

Após a criação das tabelas, foi implementado um processo de carga para PostgreSQL.

O loader:

* Percorre automaticamente os CSVs;
* Valida a compatibilidade entre CSV e tabela;
* Utiliza `COPY FROM STDIN`;
* Preserva os dados brutos;
* Não remove nulos;
* Não altera caracteres;
* Evita duplicação acidental em tabelas já carregadas.

Arquivo:

```text
src/data/load_csvs.py
```

---

## 4. Análise de Clientes

O objetivo desta etapa foi identificar clientes considerados fiéis pela combinação de:

* Faturamento total;
* Frequência de compras;
* Ticket médio;
* Diversidade de categorias.

Foram considerados elegíveis apenas clientes que compraram produtos de pelo menos **13 categorias distintas**.

### Principais resultados

| Indicador                            | Resultado    |
| ------------------------------------ | ------------ |
| Cliente com maior ticket médio       | Cliente 22   |
| Ticket médio                         | R$ 41.839,94 |
| Categorias distintas                 | 14           |
| Categoria mais consumida pelo Top 10 | Hélices      |
| Quantidade comprada                  | 492 unidades |

---

## 5. Dimensão de Calendário

Uma dimensão de datas foi criada para corrigir um problema importante na média de vendas.

Agrupar diretamente a tabela `orders` excluiria automaticamente dias sem vendas.

A abordagem utilizada foi:

```text
Dimensão calendário
        ↓
LEFT JOIN
        ↓
Vendas físicas
        ↓
COALESCE(NULL, 0)
        ↓
Média correta por dia da semana
```

### Resultado

O dia com menor média de vendas físicas foi:

> **Quinta-feira — R$ 157.154,32**

O cálculo considera também os dias em que a loja esteve aberta, mas não registrou nenhuma venda.

---

## 6. Previsão de Demanda

Produto analisado:

```text
Bússola de Bordo 702
```

Foi construído um baseline utilizando:

> **Média móvel dos três meses anteriores**

A avaliação foi feita utilizando abordagem temporal *walk-forward*, evitando utilizar informações futuras no cálculo das previsões.

### Previsões — Q1/2026

| Mês      | Demanda Real | Previsão | Erro Absoluto |
| -------- | -----------: | -------: | ------------: |
| Jan/2026 |           79 |    38,67 |         40,33 |
| Fev/2026 |           68 |    53,67 |         14,33 |
| Mar/2026 |           60 |    56,33 |          3,67 |

### Resultado

```text
Previsão total Q1/2026: 149 unidades
Demanda real Q1/2026:   207 unidades
MAE:                    19,44 unidades
```

A principal limitação observada foi a dificuldade do baseline em capturar mudanças bruscas e possíveis efeitos sazonais.

---

## 7. Sistema de Recomendação

Foi desenvolvido um recomendador baseado em similaridade entre produtos.

A matriz utilizada possui a estrutura:

```text
Cliente × Produto
```

Cada célula recebe:

```text
1 → cliente comprou o produto
0 → cliente não comprou o produto
```

Quantidade ou frequência de compra não são consideradas.

Após a construção da matriz, foi calculada a **Similaridade de Cosseno produto × produto**.

Produto de referência:

```text
Motor de Popa 1949
```

### Top 5 produtos similares

| Ranking | Produto            | Similaridade |
| ------: | ------------------ | -----------: |
|       1 | Motor de Popa 5331 |       0,2566 |
|       2 | Cabo Náutico 2105  |       0,2562 |
|       3 | Vela Mestra 1913   |       0,2558 |
|       4 | Cabo Náutico 9048  |       0,2393 |
|       5 | GPS Plotter 6249   |       0,2377 |

A principal recomendação foi:

> **Motor de Popa 5331**

---

# 📈 Dashboard

Os principais resultados foram consolidados em um dashboard desenvolvido com **Streamlit + Plotly**.

O dashboard foi dividido em três páginas.

### Visão Executiva

Apresenta:

* Quantidade de pedidos;
* Quantidade de clientes;
* Ticket médio;
* Período analisado;
* Média de vendas por dia da semana;
* Ranking de clientes fiéis;
* Insights principais.

### Clientes

Apresenta:

* Ranking por ticket médio;
* Categorias mais consumidas;
* Indicadores do segmento;
* Detalhamento dos 10 clientes selecionados.

### Modelos

Apresenta:

* Demanda real × prevista;
* MAE;
* Previsão total;
* Ranking de produtos similares;
* Resultado do sistema de recomendação.

---

## ▶️ Executando o Dashboard

Na raiz do projeto:

```bash
streamlit run dashboard/app.py
```

---

# 🚀 Como Executar o Projeto

## 1. Clone o repositório

```bash
git clone https://github.com/livmrqs/LHNauticals-Challenge.git
cd LHNauticals-Challenge
```

---

## 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## 4. Dados

Os arquivos fornecidos para o desafio estão em:

```text
data/raw/
```

Os arquivos dessa pasta são tratados como fonte e não são modificados pelas análises.

---

# 🗄️ Gerando o Schema PostgreSQL

Execute:

```bash
python src/data/generate_schema.py --input-dir data/raw --output sql/schema.sql
```

O arquivo gerado estará em:

```text
sql/schema.sql
```

---

# 📥 Carregando os Dados no PostgreSQL

O loader utiliza as seguintes variáveis de ambiente:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

Depois de configurar a conexão:

```bash
python src/data/load_csvs.py --input-dir data/raw
```

---

# 📓 Notebooks

As análises estão organizadas por etapa:

```text
notebooks/
```

| Notebook                         | Conteúdo                |
| -------------------------------- | ----------------------- |
| `01_eda.ipynb`                   | Análise exploratória    |
| `02_schema_generation.ipynb`     | Geração de schema       |
| `03_customer_analysis.ipynb`     | Análise de clientes     |
| `04_calendar_dimension.ipynb`    | Dimensão calendário     |
| `05_demand_forecasting.ipynb`    | Previsão de demanda     |
| `06_recommendation_system.ipynb` | Sistema de recomendação |

---

# 🧠 Decisões Técnicas

### Preservação dos dados brutos

Os arquivos em `data/raw/` não são alterados. Limpezas ou transformações devem acontecer em etapas posteriores.

### Grão das tabelas

As agregações foram realizadas respeitando o nível de granularidade de cada tabela.

Por exemplo, o faturamento é calculado em `orders` antes do relacionamento com `order_items`, evitando multiplicar o valor de um pedido pelo número de itens existentes nele.

### Datas sem vendas

Quando uma análise depende da existência de todos os períodos, foi criada uma dimensão calendário e utilizado `LEFT JOIN`.

Isso garante que períodos sem registro sejam representados explicitamente.

### Prevenção de Data Leakage

Na previsão de demanda, cada previsão utiliza exclusivamente dados anteriores ao período previsto.

A implementação utiliza:

```python
shift(1).rolling(3).mean()
```

evitando que o valor real do próprio mês seja utilizado na previsão.

### Sistema de recomendação

A matriz de interação é binária e representa exclusivamente presença ou ausência de compra.

A Similaridade de Cosseno representa proximidade entre padrões de compradores e **não deve ser interpretada como probabilidade de compra**.

---

# 📁 Outputs Analíticos

Os resultados utilizados pelo dashboard são exportados para:

```text
data/outputs/
```

Arquivos:

```text
elite_customers.csv
elite_category_sales.csv
weekday_sales.csv
demand_forecast.csv
product_recommendations.csv
```

Isso mantém o dashboard desacoplado das etapas de processamento realizadas nos notebooks.

---

# 📌 Resumo dos Resultados

<div align="center">

| Indicador                     | Resultado              |
| ----------------------------- | ---------------------- |
| Pedidos analisados            | **48.998**             |
| Clientes                      | **2.000**              |
| Ticket médio geral            | **R$ 28.704,99**       |
| Menor média de vendas físicas | **Quinta-feira**       |
| Cliente fiel líder            | **Cliente 22**         |
| Categoria líder do Top 10     | **Hélices**            |
| Previsão Q1/2026              | **149 unidades**       |
| MAE                           | **19,44 unidades**     |
| Principal recomendação        | **Motor de Popa 5331** |

</div>

---

## Observação

Os dados utilizados neste projeto pertencem a um cenário fictício disponibilizado exclusivamente para o desafio técnico da LH Nautical.
