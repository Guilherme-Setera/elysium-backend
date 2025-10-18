SELECT
  v.id,
  v.cliente_id,
  c.nome AS nome_cliente,
  v.forma_pagamento_id,
  f.nome AS forma_pagamento,
  v.data_venda,
  v.data_pagamento,
  v.total,
  v.valor_pago,
  v.observacao,
  v.pago,
  v.cancelada,
  v.status,
  v.a_prazo
FROM elysium.vendas v
JOIN elysium.clientes c ON c.id = v.cliente_id
JOIN elysium.formas_pagamento f ON f.id = v.forma_pagamento_id
WHERE v.id = :venda_id;
