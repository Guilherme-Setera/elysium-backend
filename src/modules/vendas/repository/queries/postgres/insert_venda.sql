INSERT INTO ambrosia.vendas (
  cliente_id,
  forma_pagamento_id,
  data_venda,
  data_pagamento,
  total,
  observacao,
  pago
) VALUES (
  :cliente_id,
  :forma_pagamento_id,
  :data_venda,
  :data_pagamento,
  :total,
  :observacao,
  :pago
)
RETURNING id;