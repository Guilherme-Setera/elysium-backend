SELECT
  v.id,
  v.cliente_id,
  c.nome AS nome_cliente,
  v.forma_pagamento_id,
  f.nome AS forma_pagamento,
  v.data_venda,
  v.data_pagamento,
  v.total,
  v.valor_pago,
  v.observacao,
  v.pago,
  v.cancelada,
  v.status,
  v.a_prazo,

  vp.datas_parcelas_pagas,
  vp.valores_parcelas_pagos,
  vp.ultima_parcela_paga,
  vp.qtd_parcelas,
  vp.qtd_parcelas_pagas

FROM elysium.vendas v
JOIN elysium.clientes c ON c.id = v.cliente_id
JOIN elysium.formas_pagamento f ON f.id = v.forma_pagamento_id

LEFT JOIN LATERAL (
  SELECT
    ARRAY_AGG(p.data_pagamento ORDER BY p.data_pagamento)
      FILTER (WHERE p.data_pagamento IS NOT NULL AND p.valor_pago > 0)               AS datas_parcelas_pagas,
    ARRAY_AGG((p.valor_pago)::numeric ORDER BY p.data_pagamento)
      FILTER (WHERE p.data_pagamento IS NOT NULL AND p.valor_pago > 0)               AS valores_parcelas_pagos,
    MAX(p.data_pagamento)
      FILTER (WHERE p.data_pagamento IS NOT NULL AND p.valor_pago > 0)               AS ultima_parcela_paga,
    COUNT(*)                                                                          AS qtd_parcelas,
    COUNT(*) FILTER (WHERE p.valor_pago > 0)                                          AS qtd_parcelas_pagas
  FROM elysium.venda_parcelas p
  WHERE p.venda_id = v.id
) vp ON TRUE

ORDER BY v.data_venda DESC;
