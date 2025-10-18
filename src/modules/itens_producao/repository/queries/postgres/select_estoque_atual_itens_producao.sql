WITH
movs AS (
  SELECT
    m.item_consumo_id,
    m.quantidade::numeric AS quantidade,
    m.preco_custo,
    m.data_movimentacao,
    m.lote,
    m.is_entrada,
    m.is_ativo
  FROM elysium.movimentacoes_estoque_itens_producao m
  WHERE DATE(m.data_movimentacao) <= :data_referencia
),
saldos AS (
  SELECT
    item_consumo_id,
    COALESCE(SUM(CASE WHEN is_entrada THEN quantidade ELSE -quantidade END), 0)::numeric AS saldo_itens,
    MAX(data_movimentacao) AS data_ult_mov
  FROM movs
  GROUP BY item_consumo_id
),
ult_preco AS (
  SELECT DISTINCT ON (item_consumo_id)
    item_consumo_id,
    preco_custo
  FROM movs
  WHERE is_entrada = TRUE
    AND preco_custo IS NOT NULL
  ORDER BY item_consumo_id, data_movimentacao DESC, lote DESC
),
proximo_lote AS (
  SELECT
    item_consumo_id,
    MIN(lote) AS lote
  FROM movs
  WHERE is_entrada = TRUE
    AND is_ativo  = TRUE
  GROUP BY item_consumo_id
)
SELECT
  ip.id AS item_producao_id,
  ip.nome AS nome_item_producao,
  COALESCE(s.saldo_itens, 0)::numeric(12,0) AS saldo_atual,
  up.preco_custo AS ultimo_preco_custo,
  s.data_ult_mov AS data_ultima_movimentacao,
  pl.lote AS proximo_lote_fifo
FROM elysium.itens_producao ip
LEFT JOIN saldos s ON s.item_consumo_id = ip.id
LEFT JOIN ult_preco up ON up.item_consumo_id = ip.id
LEFT JOIN proximo_lote pl ON pl.item_consumo_id = ip.id
ORDER BY ip.nome;
