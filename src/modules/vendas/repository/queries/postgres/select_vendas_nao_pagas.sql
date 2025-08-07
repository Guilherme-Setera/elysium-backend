SELECT
  v.id,
  v.cliente_id,
  c.nome AS nome_cliente,
  v.forma_pagamento_id,
  v.data_venda,
  v.data_pagamento,
  v.observacao,
  v.pago
FROM ambrosia.vendas v
JOIN ambrosia.clientes c ON c.id = v.cliente_id
WHERE v.pago = false
  AND v.data_pagamento <= CURRENT_DATE
ORDER BY v.data_pagamento;
