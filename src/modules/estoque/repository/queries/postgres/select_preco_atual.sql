SELECT 
  p.nome,
  pp.preco_custo,
  pp.preco_venda,
  COALESCE((
    SELECT SUM(
      CASE 
        WHEN me.tipo = 'entrada' THEN me.quantidade
        WHEN me.tipo = 'saida' THEN -me.quantidade
        ELSE 0
      END
    )
    FROM ambrosia.movimentacoes_estoque me
    WHERE me.produto_id = pp.produto_id
  ), 0) AS estoque
FROM ambrosia.produtos_precos pp
JOIN ambrosia.produtos p ON p.id = pp.produto_id
WHERE pp.produto_id = :produto_id
  AND pp.data_referencia <= :data_base
ORDER BY pp.data_referencia DESC
LIMIT 1;
