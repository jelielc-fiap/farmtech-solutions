# FarmTech Solutions - Fase 4

Protótipo de Assistente Agrícola Inteligente com ingestão IoT simulada, banco SQL, modelos de regressão em Scikit-Learn e dashboard Streamlit para gestores agrícolas.

## O que foi implementado

- Base enriquecida a partir de `pbl/fase3/sensores_fase2.csv`.
- Banco SQLite local em `data/farmtech_fase4.db`.
- Script Oracle equivalente em `sql/schema_oracle.sql`.
- Pipeline de ingestão incremental.
- Modelos de regressão para prever:
  - umidade futura;
  - pH futuro;
  - volume de irrigação;
  - necessidade de fertilização;
  - rendimento estimado.
- Dashboard Streamlit com métricas, correlações, comparação de modelos, simulador e recomendações.

## Como executar

No PowerShell, dentro da pasta `pbl/fase4`:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts\gerar_dados_iot.py
.venv\Scripts\python.exe scripts\criar_banco.py
.venv\Scripts\python.exe scripts\ingerir_dados.py
.venv\Scripts\python.exe scripts\treinar_modelos.py
.venv\Scripts\streamlit.exe run app.py
```

Também é possível iniciar a dashboard com:

```powershell
run_dashboard.bat
```

O dashboard prepara automaticamente o banco e os modelos caso ainda não existam.

## Estrutura

```text
pbl/fase4
|-- app.py
|-- requirements.txt
|-- run_dashboard.bat
|-- data/
|   |-- sensores_iot_enriquecidos.csv
|   `-- farmtech_fase4.db
|-- docs/
|   `-- roteiros_videos.md
|-- models/
|   |-- *.joblib
|   `-- metricas_modelos.json
|-- scripts/
|   |-- gerar_dados_iot.py
|   |-- criar_banco.py
|   |-- ingerir_dados.py
|   |-- treinar_modelos.py
|   `-- recomendacoes.py
`-- sql/
    |-- schema_sqlite.sql
    `-- schema_oracle.sql
```

## Pipeline de Machine Learning

O pipeline usa `ColumnTransformer` para tratar variáveis numéricas e categóricas. Os modelos comparados são:

- Regressão Linear;
- Random Forest Regressor;
- Gradient Boosting Regressor.

As métricas geradas são MAE, MSE, RMSE e R². O melhor modelo de cada alvo é salvo em `models/` com `joblib`.

## Vídeos da entrega

- [PARTE 1 CAP 1](https://www.youtube.com/watch?v=dXXKNgq7xLE)
- [PARTE 2 CAP 1](https://www.youtube.com/watch?v=KAEJDzg7NU8)
- [IR ALÉM 1 - CAP 1](https://www.youtube.com/watch?v=MECYG5PY0RE)
- [IR ALÉM 2 - CAP 1](https://www.youtube.com/watch?v=KPy6rkt4KVE)
