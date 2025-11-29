WITH vendas_mensais AS (
  SELECT
    DATE_TRUNC('month', v.data_venda) AS mes,
    v.id AS venda_id,
    v.valor_pago AS receita,
    v.data_venda
  FROM elysium.vendas v
  WHERE v.cancelada = FALSE
    AND v.pago = TRUE
    AND (:data_de IS NULL OR DATE(v.data_venda) >= :data_de)
    AND (:data_ate IS NULL OR DATE(v.data_venda) <= :data_ate)
),
custos_vendas AS (
  SELECT
    vm.mes,
    vm.venda_id,
    vm.receita,
    COALESCE(SUM(
      iv.quantidade * COALESCE((
        SELECT m.preco_custo
        FROM elysium.movimentacoes_estoque_produtos m
        WHERE m.produto_id = iv.produto_id
          AND m.tipo = 'entrada'
          AND m.preco_custo IS NOT NULL
          AND m.data_mov <= vm.data_venda
        ORDER BY m.data_mov DESC, m.id DESC
        LIMIT 1
      ), 0)
    ), 0) AS custo_total
  FROM vendas_mensais vm
  LEFT JOIN elysium.itens_venda iv ON iv.venda_id = vm.venda_id
  GROUP BY vm.mes, vm.venda_id, vm.receita
),
metricas_por_mes AS (
  SELECT
    mes,
    SUM(receita) AS receita_total,
    SUM(custo_total) AS custo_total,
    SUM(receita) - SUM(custo_total) AS lucro_total
  FROM custos_vendas
  GROUP BY mes
),
crescimento_lucro AS (
  SELECT
    mes,
    receita_total,
    custo_total,
    lucro_total,
    LAG(lucro_total) OVER (ORDER BY mes) AS lucro_mes_anterior,
    CASE
      WHEN LAG(lucro_total) OVER (ORDER BY mes) IS NULL THEN NULL
      WHEN LAG(lucro_total) OVER (ORDER BY mes) = 0 THEN
        CASE
          WHEN lucro_total > 0 THEN 100.0
          WHEN lucro_total < 0 THEN -100.0
          ELSE 0.0
        END
      ELSE
        ROUND(
          ((lucro_total - LAG(lucro_total) OVER (ORDER BY mes)) /
           ABS(LAG(lucro_total) OVER (ORDER BY mes)) * 100)::numeric,
          2
        )
    END AS taxa_crescimento_lucro_percentual
  FROM metricas_por_mes
)
SELECT
  TO_CHAR(mes, 'YYYY-MM') AS mes,
  ROUND(receita_total::numeric, 2) AS receita_total,
  ROUND(custo_total::numeric, 2) AS custo_total,
  ROUND(lucro_total::numeric, 2) AS lucro_total,
  ROUND(COALESCE(lucro_mes_anterior, 0)::numeric, 2) AS lucro_mes_anterior,
  COALESCE(taxa_crescimento_lucro_percentual, 0) AS taxa_crescimento_lucro_percentual
FROM crescimento_lucro
ORDER BY mes DESC;
