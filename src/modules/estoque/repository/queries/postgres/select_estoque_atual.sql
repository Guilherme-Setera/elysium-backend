-- select_estoque_atual.sql (preço da própria tabela)
WITH limites AS (
  SELECT
    CAST(:data_referencia AS date)                      AS dref,
    CAST(:data_referencia AS date) + INTERVAL '1 day'   AS dref_excl
)
SELECT
  p.id   AS produto_id,
  p.nome AS nome_produto,
  SUM(CASE WHEN m.tipo = 'entrada' THEN m.quantidade
           WHEN m.tipo = 'saida'   THEN -m.quantidade
           ELSE 0 END) AS saldo_estoque,

  precos.preco_custo,
  precos.preco_venda,

  COALESCE(last_mov.data_mov, MAX(m.data_mov))::date AS data_movimentacao,

  last_mov.id           AS ultima_mov_id,
  last_mov.quantidade   AS ultima_quantidade,
  last_mov.tipo         AS tipo_ultima,
  last_mov.operacao_id  AS operacao_id_ultima,
  last_mov.lote_numero  AS lote_ultimo

FROM elysium.produtos p
JOIN elysium.movimentacoes_estoque_produtos m
  ON m.produto_id = p.id
 AND m.data_mov < (SELECT dref_excl FROM limites)

LEFT JOIN LATERAL (
  SELECT mo.id, mo.quantidade, mo.tipo, mo.operacao_id, mo.data_mov, mo.lote_numero
  FROM elysium.movimentacoes_estoque_produtos mo, limites l
  WHERE mo.produto_id = p.id
    AND mo.data_mov < l.dref_excl
  ORDER BY mo.data_mov DESC, mo.id DESC
  LIMIT 1
) AS last_mov ON TRUE

LEFT JOIN LATERAL (
  SELECT mi.preco_custo, mi.preco_venda
  FROM elysium.movimentacoes_estoque_produtos mi, limites l
  WHERE mi.produto_id = p.id
    AND mi.data_mov   < l.dref_excl
    AND mi.tipo       = 'entrada'
    AND mi.preco_custo IS NOT NULL
    AND mi.preco_venda IS NOT NULL
  ORDER BY mi.data_mov DESC, mi.id DESC
  LIMIT 1
) AS precos ON TRUE

GROUP BY
  p.id, p.nome,
  last_mov.id, last_mov.quantidade, last_mov.tipo, last_mov.operacao_id, last_mov.data_mov, last_mov.lote_numero,
  precos.preco_custo, precos.preco_venda

ORDER BY p.nome;
