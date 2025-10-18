DELETE FROM elysium.movimentacoes_estoque_produtos AS m
USING elysium.operacoes_estoque AS o
WHERE m.venda_id = :venda_id
  AND m.operacao_id = o.id
  AND o.is_produto = TRUE
  AND o.tipo = 'saida'
RETURNING m.id;