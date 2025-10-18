UPDATE elysium.movimentacoes_estoque_produtos m
SET preco_custo = r.custo_unitario_produto
FROM elysium.movimentacoes_receitas r
WHERE r.produto_estoque_id = m.id
  AND m.id = :produto_mov_id;