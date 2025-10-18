UPDATE elysium.produtos
SET
    nome = COALESCE(:nome, nome),
    descricao = COALESCE(:descricao, descricao),
    validade = COALESCE(:validade, validade),
    estoque_minimo = COALESCE(:estoque_minimo, estoque_minimo)
WHERE id = :produto_id AND ativo = TRUE;