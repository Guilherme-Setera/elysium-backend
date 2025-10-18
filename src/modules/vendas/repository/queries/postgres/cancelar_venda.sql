WITH upd AS (
  UPDATE elysium.vendas
  SET
    cancelada      = TRUE,
    status         = 'cancelada',
    pago           = FALSE,
    valor_pago     = 0,
    data_pagamento = NULL
  WHERE id = :venda_id
  RETURNING id
),
del_mov AS (
  DELETE FROM elysium.movimentacoes_estoque_produtos m
  USING elysium.operacoes_estoque o
  WHERE m.venda_id = (SELECT id FROM upd)
    AND m.operacao_id = o.id
    AND o.is_produto = TRUE
    AND o.tipo = 'saida'
  RETURNING m.id
)
SELECT id FROM upd;
