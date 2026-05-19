# PBL Fase 3 - Sensores Agricolas

Repositorio organizado para a entrega da Fase 3, usando como base o arquivo `sensores_fase2.csv` da Fase 2.

## Estrutura

```text
.
|-- app.py
|-- run_dashboard.bat
|-- requirements.txt
|-- sensores_fase2.csv
|-- prints/
|   |-- 01_visualizacao_dados_csv.png
|   |-- 02_metodo_importacao.png
|   |-- 03_escolha_colunas.png
|   |-- 04_definicao_colunas.png
|   |-- 05_resumo_importacao.png
|   |-- 06_consulta_select_resultado.png
|   |-- 07_dashboard_visao_geral.png
|   |-- 08_dashboard_grafico_niveis.png
|   `-- 09_dashboard_dados_filtrados.png
|-- notebooks/
|   `-- Jeliel_RM572665_fase3_cap1.ipynb
`-- sql/
    `-- consultas_oracle.sql
```

## PBL - Project-Based Learning - FarmTech Solutions

Esta secao documenta o fluxo seguido no Oracle SQL Developer para importar o arquivo `sensores_fase2.csv`.

### Base utilizada

Foi utilizado o arquivo da Fase 2:

- `sensores_fase2.csv`

### Passos realizados

1. No Assistente de Importacao de Dados, foi selecionado o arquivo local `sensores_fase2.csv`, com formato CSV, delimitador por virgula e codificacao UTF-8.
2. O metodo de importacao escolhido foi `Inserir`, criando/importando os dados para a tabela `sensoresxlabel`.
3. As colunas do CSV foram selecionadas para importacao: `Data_Leitura`, `Umidade`, `pH`, `N_ok`, `P_ok`, `K_ok`, `Chuva_Probabilidade`, `Bomba_Ligada` e `label`.
4. Na etapa de definicao de coluna, `Data_Leitura` foi configurada como `DATE`, com formato `RRRR-MM-DD`.
5. A tela final do assistente apresentou o resumo da importacao.
6. A consulta `SELECT * FROM sensoresxlabel;` foi executada para validar os registros importados.

### Consulta realizada

```sql
SELECT * FROM sensoresxlabel;
```

O arquivo com as consultas esta em:

- `sql/consultas_oracle.sql`

## Prints do banco

### 1. Visualizacao do CSV no assistente

![Visualizacao do CSV no assistente](prints/01_visualizacao_dados_csv.png)

### 2. Metodo de importacao

![Metodo de importacao](prints/02_metodo_importacao.png)

### 3. Escolha das colunas

![Escolha das colunas](prints/03_escolha_colunas.png)

### 4. Definicao das colunas

![Definicao das colunas](prints/04_definicao_colunas.png)

### 5. Resumo da importacao

![Resumo da importacao](prints/05_resumo_importacao.png)

### 6. Consulta realizada

![Consulta realizada no Oracle](prints/06_consulta_select_resultado.png)

## Dependencias

As bibliotecas usadas estao em `requirements.txt`.

### Como executar em uma maquina nova

Depois de clonar o repositorio, acesse a pasta da Fase 3:

```powershell
cd pbl\fase3
```

Crie o ambiente virtual do Python:

```powershell
python -m venv .venv
```

Instale as dependencias do projeto:

No PowerShell:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

No Git Bash:

```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Execute a dashboard:

No PowerShell:

```powershell
.venv\Scripts\streamlit.exe run app.py
```

No Git Bash:

```bash
.venv/Scripts/streamlit.exe run app.py
```

Depois, abra no navegador o endereco exibido no terminal. Normalmente sera:

```text
http://localhost:8501
```

Tambem e possivel executar pelo arquivo:

```text
run_dashboard.bat
```

Observacao: o arquivo `run_dashboard.bat` pressupoe que o ambiente `.venv` ja foi criado e que as dependencias ja foram instaladas.

## Programa ir AlÃ©m - Dashboard em Python

O arquivo `app.py` implementa uma dashboard em Streamlit para visualizar:

- niveis de umidade, P, K e pH;
- status da irrigacao;
- sugestoes de irrigacao com base na umidade e na probabilidade de chuva.

### Como executar

```powershell
.venv\Scripts\streamlit.exe run app.py
```

Ou use o arquivo:

```text
run_dashboard.bat
```

### Prints da dashboard

#### Visao geral da dashboard

![Visao geral da dashboard](prints/07_dashboard_visao_geral.png)

#### Grafico de niveis ao longo do tempo

![Grafico de niveis ao longo do tempo](prints/08_dashboard_grafico_niveis.png)

#### Tabela de dados filtrados

![Tabela de dados filtrados](prints/09_dashboard_dados_filtrados.png)

## Programa ir AlÃ©m - Machine Learning no Agronegocio

A entrega da analise de Machine Learning esta em:

- `notebooks/Jeliel_RM572665_fase3_cap1.ipynb`

O notebook contem:

- analise exploratoria com graficos;
- identificacao do perfil ideal de solo/clima para cafe, soja e milho;
- treinamento de modelos preditivos;
- avaliacao comparativa dos modelos.

