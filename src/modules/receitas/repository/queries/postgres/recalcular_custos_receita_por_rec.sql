WITH
mp_out AS (
  SELECT
    s.materia_prima_id,
    s.lote,
    s.quantidade_estoque::numeric(12,3) AS qtd
  FROM elysium.movimentacoes_estoque_materia_prima s
  WHERE s.is_entrada = FALSE
    AND s.lote_tag   = :op_tag
),
mp_join AS (
  SELECT
    o.materia_prima_id,
    o.lote,
    o.qtd,
    e.preco_custo::numeric(12,4)        AS preco_entrada,
    e.unidade_medida
  FROM mp_out o
  JOIN elysium.movimentacoes_estoque_materia_prima e
    ON e.is_entrada       = TRUE
   AND e.materia_prima_id = o.materia_prima_id
   AND e.lote             = o.lote
),
it_out AS (
  SELECT
    o.item_consumo_id,
    o.lote,
    o.quantidade::numeric(12,3) AS qtd
  FROM elysium.movimentacoes_estoque_itens_producao o
  WHERE o.is_entrada = FALSE
    AND o.lote_tag   = :op_tag
),
it_join AS (
  SELECT
    o.item_consumo_id,
    o.qtd,
    e.preco_custo::numeric(12,4) AS preco_entrada
  FROM it_out o
  JOIN elysium.movimentacoes_estoque_itens_producao e
    ON e.is_entrada      = TRUE
   AND e.item_consumo_id = o.item_consumo_id
   AND e.lote            = o.lote
),
agg AS (
  SELECT
    /* Custo de MP proporcional ao lote (1000 g/ml) */
    COALESCE(
      SUM(
        CASE
          WHEN mp_join.unidade_medida IN ('g','ml')
            THEN (mp_join.qtd / 1000.0) * mp_join.preco_entrada
          ELSE mp_join.qtd * mp_join.preco_entrada
        END
      ),
      0
    )::numeric(12,4) AS mp_custo,

    /* Qtd de MP em “unidades” (já ficou certo na sua versão anterior; se quiser manter 1 un = 28 g/ml, troque aqui) */
    COALESCE(
      SUM(
        CASE
          WHEN mp_join.unidade_medida IN ('g','ml')
            THEN mp_join.qtd / 1000.0
          ELSE mp_join.qtd
        END
      ),
      0
    )::numeric(12,3) AS mp_qtd_unidades,

    COALESCE((SELECT SUM(qtd)               FROM it_out ), 0)::numeric(12,3) AS it_qtd,
    COALESCE((SELECT SUM(qtd * preco_entrada) FROM it_join), 0)::numeric(12,4) AS it_custo
  FROM mp_join
)
UPDATE elysium.movimentacoes_receitas mr
SET
  quantidade_materia_prima  = a.mp_qtd_unidades,
  custo_materia_prima       = a.mp_custo,
  quantidade_itens_producao = a.it_qtd,
  custo_itens_producao      = a.it_custo
FROM agg a
WHERE mr.id = :rec_id;
