UPDATE elysium.vendas
SET
  valor_pago = COALESCE(valor_pago, 0) + :valor_pago,
  pago = CASE
           WHEN COALESCE(valor_pago, 0) + :valor_pago >= COALESCE(total, 0)
           THEN TRUE
           ELSE FALSE
         END,
  data_pagamento = CASE
                     WHEN COALESCE(valor_pago, 0) + :valor_pago >= COALESCE(total, 0)
                     THEN COALESCE(:data_pagamento, CURRENT_TIMESTAMP)
                     ELSE data_pagamento
                   END
WHERE id = :venda_id
  AND cancelada = FALSE
RETURNING id, pago, valor_pago;