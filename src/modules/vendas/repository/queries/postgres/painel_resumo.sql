SELECT
  SUM(total) FILTER (WHERE data_venda = CURRENT_DATE) AS total_diario,
  SUM(total) FILTER (WHERE DATE_TRUNC('month', data_venda) = DATE_TRUNC('month', CURRENT_DATE)) AS total_mensal,
  COUNT(*) AS quantidade_vendas
FROM ambrosia.vendas
WHERE data_venda BETWEEN :inicio AND :fim;