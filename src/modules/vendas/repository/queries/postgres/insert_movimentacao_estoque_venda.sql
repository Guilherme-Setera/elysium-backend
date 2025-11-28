WITH RECURSIVE
operacao_info AS (
  SELECT oe.tipo
  FROM elysium.operacoes_estoque oe
  WHERE oe.id = :operacao_id
),
lotes_disponiveis AS (
  SELECT
    m.lote_numero,
    SUM(CASE
      WHEN m.tipo = 'entrada' THEN m.quantidade
      WHEN m.tipo = 'saida' THEN -m.quantidade
      ELSE 0
    END) AS saldo_disponivel,
    MIN(m.data_mov) AS data_entrada_lote,
    ROW_NUMBER() OVER (ORDER BY MIN(m.data_mov), m.lote_numero) AS ordem_fifo
  FROM elysium.movimentacoes_estoque_produtos m
  WHERE m.produto_id = :produto_id
    AND m.lote_numero IS NOT NULL
    AND m.data_mov <= COALESCE(:data_mov, CURRENT_TIMESTAMP)
  GROUP BY m.lote_numero
  HAVING SUM(CASE
    WHEN m.tipo = 'entrada' THEN m.quantidade
    WHEN m.tipo = 'saida' THEN -m.quantidade
    ELSE 0
  END) > 0
),
distribuicao_fifo AS (
  SELECT
    lote_numero,
    saldo_disponivel,
    data_entrada_lote,
    ordem_fifo,
    LEAST(:quantidade, saldo_disponivel) AS quantidade_consumida,
    :quantidade - LEAST(:quantidade, saldo_disponivel) AS quantidade_restante
  FROM lotes_disponiveis
  WHERE ordem_fifo = 1

  UNION ALL

  SELECT
    ld.lote_numero,
    ld.saldo_disponivel,
    ld.data_entrada_lote,
    ld.ordem_fifo,
    LEAST(df.quantidade_restante, ld.saldo_disponivel) AS quantidade_consumida,
    df.quantidade_restante - LEAST(df.quantidade_restante, ld.saldo_disponivel) AS quantidade_restante
  FROM distribuicao_fifo df
  JOIN lotes_disponiveis ld ON ld.ordem_fifo = df.ordem_fifo + 1
  WHERE df.quantidade_restante > 0
)
INSERT INTO elysium.movimentacoes_estoque_produtos (
  produto_id,
  quantidade,
  operacao_id,
  tipo,
  data_mov,
  venda_id,
  lote_numero,
  data_validade,
  preco_custo,
  preco_venda
)
SELECT
  :produto_id,
  df.quantidade_consumida,
  :operacao_id,
  oi.tipo,
  COALESCE(:data_mov, CURRENT_TIMESTAMP),
  COALESCE(CAST(:venda_id AS INTEGER), NULL),
  df.lote_numero,
  NULL,
  NULL,
  NULL
FROM distribuicao_fifo df
CROSS JOIN operacao_info oi
WHERE oi.tipo = 'saida'
  AND df.quantidade_consumida > 0
ORDER BY df.ordem_fifo;
