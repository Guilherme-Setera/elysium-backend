SELECT 
  v.id AS venda_id,
  v.cliente_id, 
  v.data_venda,
  v.total,
  v.forma_pagamento,
  c.nome AS cliente_nome,
  iv.id AS item_id,
  iv.produto_id,
  p.nome AS nome_produto,
  iv.quantidade,
  iv.preco_unitario,
  iv.subtotal
FROM ambrosia.vendas v
LEFT JOIN ambrosia.clientes c ON v.cliente_id = c.id
LEFT JOIN ambrosia.itens_venda iv ON iv.venda_id = v.id
LEFT JOIN ambrosia.produtos p ON p.id = iv.produto_id
WHERE v.id = :venda_id;
