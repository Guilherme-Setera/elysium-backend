WITH
params AS (
  SELECT
    CAST(:receita_id AS int)                                              AS receita_id,
    COALESCE(CAST(:data_mov AS timestamp), CURRENT_TIMESTAMP)             AS data_mov,
    (date_trunc('day', COALESCE(CAST(:data_mov AS timestamp), CURRENT_TIMESTAMP)) + interval '23:59:59.999') AS data_mov_fim_dia,
    CAST(:preco_venda AS numeric(12,2))                                   AS preco_venda,
    CAST(:consumos_json AS jsonb)                                         AS consumos_json,
    CAST(:produto_final_json AS jsonb)                                    AS produto_final_json,
    gen_random_uuid()::text                                               AS op_tag
),
prod AS (
  SELECT r.produto_id
  FROM elysium.receitas r
  JOIN params p ON p.receita_id = r.id
),
mp_rows AS (
  SELECT
    (x->>'materia_prima_id')::int            AS materia_prima_id,
    (x->>'quantidade')::numeric(12,3)        AS quantidade,
    NULLIF(x->>'unidade','')                 AS unidade
  FROM params p
  CROSS JOIN LATERAL jsonb_array_elements(COALESCE(p.consumos_json->'materias_primas','[]'::jsonb)) AS x
),
it_rows AS (
  SELECT
    (x->>'item_producao_id')::int            AS item_producao_id,
    (x->>'quantidade_itens')::int            AS quantidade_itens
  FROM params p
  CROSS JOIN LATERAL jsonb_array_elements(COALESCE(p.consumos_json->'itens_producao','[]'::jsonb)) AS x
),
mp_do AS (
  INSERT INTO elysium.movimentacoes_estoque_materia_prima(
    materia_prima_id, quantidade_estoque, data_mov, operacao_id,
    quantidade_unidade, lote, lote_tag, preco_custo, unidade_medida,
    is_entrada, is_ativo, receita_id
  )
  SELECT
    m.materia_prima_id,
    m.quantidade,
    p.data_mov_fim_dia,
    8,
    0,
    NULL,
    p.op_tag,
    NULL,
    COALESCE(
      m.unidade,
      (SELECT unidade_base FROM elysium.materias_prima mpb WHERE mpb.id = m.materia_prima_id)
    ),
    FALSE,
    NULL,
    p.receita_id
  FROM mp_rows m, params p
  WHERE m.quantidade > 0
  RETURNING id
),
it_do AS (
  INSERT INTO elysium.movimentacoes_estoque_itens_producao(
    item_consumo_id, quantidade, data_movimentacao, lote, is_entrada,
    receita_id, is_ativo, descricao, preco_custo, lote_tag
  )
  SELECT
    i.item_producao_id,
    i.quantidade_itens,
    p.data_mov_fim_dia,
    NULL,
    FALSE,
    p.receita_id,
    NULL,
    'Consumo p/ receita ' || p.op_tag,
    NULL,
    p.op_tag
  FROM it_rows i, params p
  WHERE i.quantidade_itens > 0
  RETURNING id
),
prod_in AS (
  INSERT INTO elysium.movimentacoes_estoque_produtos (
    produto_id, quantidade, tipo, operacao_id, data_mov, preco_venda
  )
  SELECT pr.produto_id,
         (p.produto_final_json->>'quantidade_unidades')::int,
         'entrada', 10, p.data_mov,
         COALESCE((p.produto_final_json->>'preco_venda')::numeric(12,2), p.preco_venda)
  FROM params p
  JOIN prod pr ON TRUE
  WHERE p.produto_final_json IS NOT NULL
  RETURNING id AS produto_estoque_id, produto_id
),
rec_ins AS (
  INSERT INTO elysium.movimentacoes_receitas (
    receita_id, produto_id, data_execucao,
    quantidade_materia_prima, custo_materia_prima,
    quantidade_itens_producao, custo_itens_producao,
    produto_estoque_id, quantidade_produto, is_meia_receita
  )
  SELECT
    p.receita_id,
    pr.produto_id,
    p.data_mov,
    0, 0, 0, 0,
    (SELECT produto_estoque_id FROM prod_in LIMIT 1),
    COALESCE((p.produto_final_json->>'quantidade_unidades')::int, 0),
    FALSE
  FROM params p
  JOIN prod pr ON TRUE
  RETURNING id
),
mp_sum AS (
  SELECT COALESCE(SUM(quantidade),0)::numeric(12,3) AS total FROM mp_rows
),
it_sum AS (
  SELECT COALESCE(SUM(quantidade_itens),0)::int AS total FROM it_rows
)
SELECT
  (SELECT id FROM rec_ins)                         AS rec_id,
  (SELECT produto_estoque_id FROM prod_in LIMIT 1) AS produto_mov_id,
  (SELECT total FROM mp_sum)                       AS mp_qtd_consumida,
  (SELECT total FROM it_sum)                       AS it_qtd_consumida,
  (SELECT op_tag FROM params)                      AS op_tag;
