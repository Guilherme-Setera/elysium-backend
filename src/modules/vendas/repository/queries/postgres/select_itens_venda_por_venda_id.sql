SELECT
  iv.id,
  iv.venda_id,
  iv.produto_id,
  p.nome AS nome_produto,
  iv.quantidade,
  iv.preco_unitario,
  iv.subtotal,
  v.status,
  v.cancelada,
  v.data_venda,
  v.frete,
  v.codigo_rastreio,
  v.data_entrega,
  SUM(iv.subtotal) OVER (PARTITION BY iv.venda_id)                              AS total_itens,
  (SUM(iv.subtotal) OVER (PARTITION BY iv.venda_id) + COALESCE(v.frete, 0))     AS total_com_frete
FROM elysium.itens_venda iv
JOIN elysium.produtos p ON p.id = iv.produto_id
JOIN elysium.vendas  v ON v.id = iv.venda_id
WHERE iv.venda_id = :venda_id
ORDER BY iv.id;