SELECT
  m.produto_id,
  p.nome AS nome_produto,
  m.data_mov AS data_movimentacao,
  m.quantidade,
  m.preco_custo,
  (m.quantidade * COALESCE(m.preco_custo, 0)) AS custo_total
FROM elysium.movimentacoes_estoque_produtos m
JOIN elysium.produtos p ON p.id = m.produto_id
LEFT JOIN elysium.operacoes_estoque o ON o.id = m.operacao_id
WHERE m.tipo = 'entrada'
  AND m.data_mov BETWEEN :data_inicio AND :data_fim
  AND m.preco_custo IS NOT NULL
ORDER BY m.data_mov DESC;