SELECT id, nome, ativo, estoque_minimo
FROM elysium.itens_producao
WHERE (:somente_ativos IS NULL) OR (ativo = :somente_ativos)
ORDER BY nome;