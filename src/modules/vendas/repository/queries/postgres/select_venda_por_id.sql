SELECT
  v.id AS id, 
  v.cliente_id,
  c.nome AS nome_cliente,
  v.forma_pagamento_id,
  f.nome AS forma_pagamento,
  v.data_venda,
  v.data_pagamento,
  v.total,
  v.observacao,
  v.pago,
  v.cancelada
FROM ambrosia.vendas v
JOIN ambrosia.clientes c ON c.id = v.cliente_id
JOIN ambrosia.formas_pagamento f ON f.id = v.forma_pagamento_id
WHERE v.id = :venda_id;