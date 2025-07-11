SELECT 
  DATE(v.data_venda) AS data,
  COUNT(*) AS total_vendas,
  SUM(v.total) AS valor_total
FROM ambrosia.vendas v
WHERE 
  v.data_venda BETWEEN :data_inicio AND :data_fim
GROUP BY DATE(v.data_venda)
ORDER BY data;
