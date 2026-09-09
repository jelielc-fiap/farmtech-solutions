# Entrega 1 — Rendimento agrícola

[Notebook executado](notebooks/JelielCardoso_RM572665_pbl_fase4.ipynb) · [Vídeo](https://www.youtube.com/watch?v=dIXJ3ubKnV8)

O relatório completo está no notebook. O CSV oficial está em data/crop_yield.csv e sua procedência/hash em data/origem_dataset.json. São 156 registros e seis colunas, sem ausentes ou duplicatas completas. As unidades originais são preservadas.

A solução contém EDA, KMeans, Isolation Forest e cinco regressões (Linear, Ridge, Random Forest, Gradient Boosting, Extra Trees). O Pipeline é ajustado no treino; cenários climáticos inteiros são separados e o algoritmo é escolhido por validação cruzada agrupada. O notebook discute métricas globais e por cultura, baseline, pontos fortes e limitações.

## Reprodução

Na pasta principal da entrega, instale requirements.txt em um ambiente Python 3.12 e execute:

```powershell
.\.venv\Scripts\python.exe entrega1_ml/scripts/gerar_notebook.py
```

O script carrega o CSV oficial, executa a análise, gera saídas/modelo e salva o notebook executado. Mantenha data, scripts, outputs e models na estrutura fornecida. O arquivo gerar_crop_yield.py é apenas um utilitário legado de demonstração, não é a fonte dos resultados oficiais nem é chamado pelo fluxo de entrega.

O arquivo do notebook mantém pbl_fase4.ipynb por exigência literal do enunciado.
