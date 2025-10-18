UPDATE elysium.vendas
SET
  cliente_id         = :cliente_id,
  forma_pagamento_id = :forma_pagamento_id,
  data_venda         = :data_venda,
  total              = :total,
  frete              = :frete,
  observacao         = :observacao,
  data_entrega       = :data_entrega,
  codigo_rastreio    = :codigo_rastreio,
  a_prazo            = :a_prazo,
  data_pagamento = CASE
                     WHEN :data_pagamento IS NOT NULL
                       THEN :data_pagamento
                     WHEN COALESCE(valor_pago, 0) >= (COALESCE(:total, 0) + COALESCE(:frete, 0))
                       THEN COALESCE(data_pagamento, CURRENT_TIMESTAMP)
                     ELSE data_pagamento
                   END,
  pago = CASE
           WHEN :data_pagamento IS NOT NULL
             THEN TRUE
           WHEN COALESCE(valor_pago, 0) >= (COALESCE(:total, 0) + COALESCE(:frete, 0))
             THEN TRUE
           ELSE FALSE
         END
WHERE id = :venda_id
  AND cancelada = FALSE
RETURNING id, pago, data_pagamento;