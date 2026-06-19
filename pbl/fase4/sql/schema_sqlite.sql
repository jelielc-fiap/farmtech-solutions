CREATE TABLE IF NOT EXISTS execucoes_ingestao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    executado_em TEXT NOT NULL,
    arquivo_origem TEXT NOT NULL,
    registros_lidos INTEGER NOT NULL,
    registros_inseridos INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS leituras_sensores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_leitura TEXT NOT NULL,
    cultura TEXT NOT NULL,
    umidade REAL NOT NULL,
    ph REAL NOT NULL,
    n_ok INTEGER NOT NULL,
    p_ok INTEGER NOT NULL,
    k_ok INTEGER NOT NULL,
    chuva_probabilidade REAL NOT NULL,
    bomba_ligada INTEGER NOT NULL,
    umidade_futura REAL NOT NULL,
    ph_futuro REAL NOT NULL,
    volume_irrigacao_l REAL NOT NULL,
    necessidade_fertilizacao_kg_ha REAL NOT NULL,
    rendimento_estimado_t_ha REAL NOT NULL,
    UNIQUE (data_leitura, cultura)
);

CREATE TABLE IF NOT EXISTS previsoes_modelo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    leitura_id INTEGER NOT NULL,
    modelo TEXT NOT NULL,
    alvo TEXT NOT NULL,
    valor_previsto REAL NOT NULL,
    criado_em TEXT NOT NULL,
    FOREIGN KEY (leitura_id) REFERENCES leituras_sensores(id)
);

CREATE TABLE IF NOT EXISTS recomendacoes_manejo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    leitura_id INTEGER NOT NULL,
    acao_irrigacao TEXT NOT NULL,
    acao_ph TEXT NOT NULL,
    acao_nutrientes TEXT NOT NULL,
    risco_produtivo TEXT NOT NULL,
    justificativa TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    FOREIGN KEY (leitura_id) REFERENCES leituras_sensores(id)
);
