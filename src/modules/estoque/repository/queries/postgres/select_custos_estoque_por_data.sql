SELECT
  m.produto_id,
  p.nome AS nome_produto,
  m.data_mov AS data_movimentacao,
  m.quantidade,
  preco.preco_custo,
  (m.quantidade * preco.preco_custo) AS custo_total
FROM elysium.movimentacoes_estoque m
JOIN elysium.produtos p ON p.id = m.produto_id
JOIN elysium.operacoes_estoque o ON o.id = m.operacao_id
LEFT JOIN LATERAL (
  SELECT pp.preco_custo
  FROM elysium.produtos_precos pp
  WHERE pp.produto_id = m.produto_id
    AND pp.data_referencia <= m.data_mov
  ORDER BY pp.data_referencia DESC
  LIMIT 1
) preco ON true
WHERE o.tipo = 'entrada'
  AND m.data_mov BETWEEN :data_inicio AND :data_fim
ORDER BY m.data_mov DESC;