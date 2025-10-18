INSERT INTO elysium.itens_producao (nome, ativo, estoque_minimo)
VALUES (TRIM(:nome), COALESCE(:ativo, TRUE), :estoque_minimo)
RETURNING id