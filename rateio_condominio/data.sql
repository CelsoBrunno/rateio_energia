-- condominio_black_falcon/data.sql

-- Limpa dados existentes para garantir consistência ao rodar init-db múltiplas vezes
DELETE FROM Unidades; 

INSERT INTO Unidades (nome, tipo, ultima_leitura_kwh) VALUES
('Casa 1', 'casa', 100),    -- Leitura inicial Exemplo
('Casa 2', 'casa', 1000),   -- Leitura inicial Exemplo
('Casa 3', 'casa', 0),
('Casa 4', 'casa', 0),
('Casa 5', 'casa', 0),
('Casa 6', 'casa', 0),
('Casa 7', 'casa', 0),
('Casa 8', 'casa', 0),
('Casa 9', 'casa', 0),
('Casa 10', 'casa', 0),
('Salão de Festas', 'salao_festas', 0); -- Para o salão, esta coluna não será usada da mesma forma, mas mantemos por consistência da tabela.