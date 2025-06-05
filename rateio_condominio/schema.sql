-- condominio_black_falcon/schema.sql

DROP TABLE IF EXISTS DetalhesRateioUnidade;
DROP TABLE IF EXISTS Contas;
DROP TABLE IF EXISTS Unidades;

CREATE TABLE Unidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL, -- 'casa' ou 'salao_festas'
    ultima_leitura_kwh REAL DEFAULT 0 -- NOVA COLUNA: Armazena a última leitura do medidor para casas
);

CREATE TABLE Contas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mes_referencia INTEGER NOT NULL,
    ano_referencia INTEGER NOT NULL,
    valor_total_reais REAL NOT NULL,
    consumo_total_interno_kwh REAL,
    custo_medio_kwh REAL,
    custo_total_salao_reais REAL,
    cota_salao_por_casa_reais REAL,
    data_lancamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mes_referencia, ano_referencia)
);

CREATE TABLE DetalhesRateioUnidade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conta_id INTEGER NOT NULL,
    unidade_id INTEGER NOT NULL,
    leitura_anterior_kwh REAL, -- NOVA COLUNA (para casas)
    leitura_atual_kwh REAL,    -- NOVA COLUNA (para casas, para salão é o consumo direto)
    consumo_kwh REAL NOT NULL, -- Consumo calculado para casas, ou direto para salão
    custo_direto_reais REAL,
    valor_final_reais REAL,
    FOREIGN KEY (conta_id) REFERENCES Contas (id),
    FOREIGN KEY (unidade_id) REFERENCES Unidades (id)
);