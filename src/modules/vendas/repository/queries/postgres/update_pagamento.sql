UPDATE elysium.vendas
SET
  valor_pago = COALESCE(total, valor_pago, 0),
  pago = TRUE,
  data_pagamento = COALESCE(data_pagamento, CURRENT_TIMESTAMP)
WHERE id = :venda_id
  AND cancelada = FALSE
RETURNING id, pago, valor_pago;
