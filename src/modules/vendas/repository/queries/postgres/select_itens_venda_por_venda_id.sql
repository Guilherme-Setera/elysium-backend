SELECT
  iv.id,
  iv.venda_id,
  iv.produto_id,
  p.nome AS nome_produto,
  iv.quantidade,
  iv.preco_unitario,
  iv.subtotal
FROM ambrosia.itens_venda iv
JOIN ambrosia.produtos p ON iv.produto_id = p.id
WHERE iv.venda_id = :venda_id
ORDER BY iv.id;
