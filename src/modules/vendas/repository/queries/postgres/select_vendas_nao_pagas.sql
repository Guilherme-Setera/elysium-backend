SELECT
  v.id,
  v.cliente_id,
  c.nome AS nome_cliente,
  v.forma_pagamento_id,
  fp.nome AS forma_pagamento,
  v.data_venda,
  v.data_pagamento,
  v.total,
  v.frete,
  (COALESCE(v.total, 0) + COALESCE(v.frete, 0)) AS total_com_frete,
  v.observacao,
  v.pago,
  v.cancelada,
  v.a_prazo,
  COALESCE(v.valor_pago, 0) AS valor_pago,
  v.codigo_rastreio,
  v.data_entrega,
  CASE
    WHEN v.cancelada THEN 'cancelada'
    WHEN v.a_prazo THEN
      CASE
        WHEN COALESCE(v.valor_pago, 0) >= (COALESCE(v.total, 0) + COALESCE(v.frete, 0)) THEN 'quitada'
        WHEN COALESCE(v.valor_pago, 0) > 0 THEN 'parcial'
        ELSE 'aberta'
      END
    ELSE
      CASE
        WHEN v.pago THEN 'paga'
        ELSE 'a pagar'
      END
  END AS status
FROM elysium.vendas v
JOIN elysium.clientes c        ON c.id  = v.cliente_id
LEFT JOIN elysium.formas_pagamento fp ON fp.id = v.forma_pagamento_id
WHERE v.cancelada = false
  AND (
        (v.a_prazo = true  AND COALESCE(v.valor_pago, 0) < (COALESCE(v.total, 0) + COALESCE(v.frete, 0)))
     OR (v.a_prazo = false AND v.pago = false)
      )
  AND (v.data_pagamento IS NULL OR v.data_pagamento <= CURRENT_DATE)
ORDER BY v.data_pagamento NULLS LAST, v.data_venda;
