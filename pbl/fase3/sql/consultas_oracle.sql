-- Consulta usada para validar a importacao do CSV no Oracle SQL Developer.
-- A tabela foi criada pelo Assistente de Importacao de Dados.

SELECT * FROM sensoresxlabel;

-- Consultas auxiliares sugeridas para conferencia:
SELECT COUNT(*) AS total_registros FROM sensoresxlabel;

SELECT label, COUNT(*) AS total
FROM sensoresxlabel
GROUP BY label
ORDER BY total DESC;
