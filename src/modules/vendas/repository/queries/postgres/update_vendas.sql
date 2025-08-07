UPDATE ambrosia.vendas
SET
  cliente_id = :cliente_id,
  data_venda = :data_venda,
  total = :total,
  forma_pagamento_id = :forma_pagamento_id,
  observacao = :observacao,
  data_pagamento = :data_pagamento,
  pago = CASE
    WHEN :data_pagamento IS NOT NULL AND :data_pagamento <= CURRENT_TIMESTAMP THEN true
    ELSE false
  END
WHERE id = :venda_id;
