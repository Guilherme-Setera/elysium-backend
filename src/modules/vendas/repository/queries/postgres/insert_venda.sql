INSERT INTO elysium.vendas (
  cliente_id,
  forma_pagamento_id,
  data_venda,
  data_pagamento,
  total,
  observacao,
  frete,
  pago,
  a_prazo,
  data_entrega,
  codigo_rastreio,
  valor_pago
) VALUES (
  :cliente_id,
  :forma_pagamento_id,
  :data_venda,
  :data_pagamento,
  :total,
  :observacao,
  COALESCE(:frete, 0),
  COALESCE(:pago, FALSE),
  COALESCE(:a_prazo, FALSE),
  :data_entrega,
  :codigo_rastreio,
  COALESCE(:valor_pago, 0)
)
RETURNING id;
