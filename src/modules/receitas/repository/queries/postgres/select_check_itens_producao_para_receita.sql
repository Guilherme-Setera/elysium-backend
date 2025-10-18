WITH saldo_itens AS (
  SELECT
    meip.item_consumo_id AS item_id,
    COALESCE(SUM(CASE WHEN COALESCE(meip.is_entrada, TRUE)
                      THEN meip.quantidade ELSE -meip.quantidade END), 0) AS estoque_atual
  FROM elysium.movimentacoes_estoque_itens_producao meip
  GROUP BY meip.item_consumo_id
)
SELECT
  ip.id AS item_id,
  ip.nome AS nome,
  COALESCE(s.estoque_atual, 0) AS estoque_atual,
  (ir.quantidade_itens * COALESCE(:quantidade, 1)
     * CASE WHEN COALESCE(:is_meia_receita, FALSE) THEN 0.5 ELSE 1 END
  )::numeric(12,3) AS consumo_necessario
FROM elysium.itens_receita ir
JOIN elysium.itens_producao ip ON ip.id = ir.item_producao_id
LEFT JOIN saldo_itens s        ON s.item_id = ir.item_producao_id
WHERE ir.receita_id = :receita_id
  AND ir.item_producao_id IS NOT NULL;
