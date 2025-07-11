INSERT INTO ambrosia.vendas (
  cliente_id,
  data_venda,
  total,
  forma_pagamento
)
VALUES (
  :cliente_id,
  :data_venda,
  :total,
  :forma_pagamento
)
RETURNING id;
