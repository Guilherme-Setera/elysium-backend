SELECT 
  v.id AS venda_id,
  v.cliente_id,
  v.data_venda,
  v.total,
  v.forma_pagamento,

  iv.id AS item_id,
  iv.produto_id,
  iv.quantidade,
  iv.preco_unitario,
  iv.subtotal

FROM ambrosia.vendas v
LEFT JOIN ambrosia.itens_venda iv ON iv.venda_id = v.id
WHERE 
  (:cliente_id IS NULL OR v.cliente_id = :cliente_id)
  AND (:data_inicio IS NULL OR v.data_venda >= :data_inicio)
  AND (:data_fim IS NULL OR v.data_venda <= :data_fim)
  AND (:forma_pagamento IS NULL OR v.forma_pagamento = :forma_pagamento)
ORDER BY v.data_venda DESC, v.id, iv.id;
