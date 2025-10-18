-- select_preco_atual.sql (usa movimentacoes_estoque_produtos)
WITH limites AS (
  SELECT
    CAST(:data_base AS date)                      AS dref,
    CAST(:data_base AS date) + INTERVAL '1 day'   AS dref_excl
)
SELECT
  p.nome,
  precos.preco_custo,
  precos.preco_venda,
  COALESCE(
    SUM(
      CASE
        WHEN m.tipo = 'entrada' THEN m.quantidade
        WHEN m.tipo = 'saida'   THEN -m.quantidade
        ELSE 0
      END
    ), 0
  ) AS estoque
FROM elysium.produtos p
LEFT JOIN elysium.movimentacoes_estoque_produtos m
  ON m.produto_id = p.id
 AND m.data_mov < (SELECT dref_excl FROM limites)
LEFT JOIN LATERAL (
  SELECT mi.preco_custo, mi.preco_venda
  FROM elysium.movimentacoes_estoque_produtos mi, limites l
  WHERE mi.produto_id   = p.id
    AND mi.tipo         = 'entrada'
    AND mi.preco_custo IS NOT NULL
    AND mi.preco_venda IS NOT NULL
    AND mi.data_mov    < l.dref_excl
  ORDER BY mi.data_mov DESC, mi.id DESC
  LIMIT 1
) AS precos ON TRUE
WHERE p.id = :produto_id
GROUP BY p.nome, precos.preco_custo, precos.preco_venda;
