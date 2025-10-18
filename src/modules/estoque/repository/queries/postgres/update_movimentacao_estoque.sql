UPDATE elysium.movimentacoes_estoque
SET
    produto_id  = COALESCE(:produto_id, produto_id),
    tipo        = COALESCE(:tipo, tipo),
    quantidade  = COALESCE(:quantidade, quantidade),
    data_mov    = COALESCE(:data_mov, data_mov),
    operacao_id = COALESCE(:operacao_id, operacao_id)
WHERE id = :id
  AND venda_id IS NULL
RETURNING id, produto_id, tipo, data_mov, operacao_id;