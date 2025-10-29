WITH
mp_out AS (
  SELECT
    s.materia_prima_id,
    s.lote,
    s.quantidade_estoque::numeric(12,3) AS qtd,
    e.preco_custo::numeric(12,4)        AS preco_entrada,
    e.unidade_medida
  FROM elysium.movimentacoes_estoque_materia_prima s
  JOIN elysium.movimentacoes_estoque_materia_prima e
    ON e.is_entrada       = TRUE
   AND e.materia_prima_id = s.materia_prima_id
   AND e.lote             = s.lote
  WHERE s.is_entrada = FALSE
    AND s.lote_tag   = :op_tag
),
it_out AS (
  SELECT
    o.item_consumo_id,
    o.lote,
    o.quantidade::numeric(12,3) AS qtd,
    e.preco_custo::numeric(12,4) AS preco_entrada
  FROM elysium.movimentacoes_estoque_itens_producao o
  JOIN elysium.movimentacoes_estoque_itens_producao e
    ON e.is_entrada      = TRUE
   AND e.item_consumo_id = o.item_consumo_id
   AND e.lote            = o.lote
  WHERE o.is_entrada = FALSE
    AND o.lote_tag   = :op_tag
),
agg AS (
  SELECT
    COALESCE(
      SUM(
        CASE
          WHEN mp_out.unidade_medida IN ('g','ml')
            THEN (mp_out.qtd / 1000.0) * mp_out.preco_entrada
          ELSE mp_out.qtd * mp_out.preco_entrada
        END
      ),
      0
    )::numeric(12,4) AS mp_custo,
    COALESCE(SUM(mp_out.qtd), 0)::numeric(12,3) AS mp_qtd_unidades,
    COALESCE((SELECT SUM(qtd) FROM it_out), 0)::numeric(12,3) AS it_qtd,
    COALESCE((SELECT SUM(qtd * preco_entrada) FROM it_out), 0)::numeric(12,4) AS it_custo
  FROM mp_out
)
UPDATE elysium.movimentacoes_receitas mr
SET
  quantidade_materia_prima  = a.mp_qtd_unidades,
  custo_materia_prima       = a.mp_custo,
  quantidade_itens_producao = a.it_qtd,
  custo_itens_producao      = a.it_custo
FROM agg a
WHERE mr.id = :rec_id;
