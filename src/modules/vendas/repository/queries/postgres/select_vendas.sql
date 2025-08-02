SELECT
  v.id,
  v.cliente_id,
  c.nome AS nome_cliente,
  v.forma_pagamento_id,
  f.nome AS forma_pagamento,
  v.data_venda,
  v.data_pagamento,
  v.total,
  v.observacao
FROM ambrosia.vendas v
LEFT JOIN ambrosia.clientes c ON v.cliente_id = c.id
LEFT JOIN ambrosia.formas_pagamento f ON v.forma_pagamento_id = f.id
ORDER BY v.data_venda DESC;
