SELECT 
  iv.produto_id,
  p.nome AS nome_produto,
  SUM(iv.quantidade) AS total_vendido,
  SUM(iv.subtotal) AS total_faturado
FROM ambrosia.itens_venda iv
JOIN ambrosia.produtos p ON p.id = iv.produto_id
JOIN ambrosia.vendas v ON v.id = iv.venda_id
WHERE 
  v.data_venda BETWEEN :data_inicio AND :data_fim
GROUP BY iv.produto_id, p.nome
ORDER BY total_faturado DESC;
