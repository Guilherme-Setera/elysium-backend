UPDATE ambrosia.vendas
SET 
  cliente_id = :cliente_id,
  forma_pagamento = :forma_pagamento,
  total = :total
WHERE id = :venda_id;
