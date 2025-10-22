WITH
params AS (
  SELECT
    CAST(:receita_id AS int) AS receita_id,
    CAST(:qtd_prod   AS int) AS qtd_prod,
    CAST(:is_meia    AS boolean) AS is_meia,
    CAST(:preco_venda AS numeric(12,2)) AS preco_venda,
    COALESCE(CAST(:data_mov AS timestamp), CURRENT_TIMESTAMP) AS data_mov,
    (date_trunc('day', COALESCE(CAST(:data_mov AS timestamp), CURRENT_TIMESTAMP)) + interval '23:59:59.999') AS data_mov_fim_dia,
    CASE WHEN CAST(:is_meia AS boolean) THEN 0.5::numeric ELSE 1.0::numeric END AS fator_mp,
    gen_random_uuid()::text AS op_tag
),
mp_rows AS (
  SELECT
    ir.materia_prima_id,
    (ir.quantidade * p.fator_mp * p.qtd_prod)::numeric(12,3) AS qtd,
    ir.unidade AS unidade_mp
  FROM elysium.itens_receita ir
  JOIN params p ON p.receita_id = ir.receita_id
  WHERE ir.receita_id = p.receita_id
    AND ir.materia_prima_id IS NOT NULL
    AND ir.quantidade IS NOT NULL AND ir.quantidade > 0
),
mp_do AS (
  INSERT INTO elysium.movimentacoes_estoque_materia_prima (
    materia_prima_id, quantidade_estoque, data_mov, operacao_id,
    quantidade_unidade, lote, lote_tag, preco_custo, unidade_medida,
    is_entrada, is_ativo, receita_id
  )
  SELECT
    m.materia_prima_id,
    m.qtd,
    (SELECT data_mov_fim_dia FROM params),
    8,
    0,
    NULL,
    (SELECT op_tag FROM params),
    NULL,
    m.unidade_mp,
    FALSE,
    NULL,
    (SELECT receita_id FROM params)
  FROM mp_rows m
  WHERE m.qtd > 0
  RETURNING id
),
it_rows AS (
  SELECT
    ir.item_producao_id,
    (ir.quantidade_itens * p.qtd_prod)::int AS qtd
  FROM elysium.itens_receita ir
  JOIN params p ON p.receita_id = ir.receita_id
  WHERE ir.receita_id = p.receita_id
    AND ir.item_producao_id IS NOT NULL
    AND ir.quantidade_itens IS NOT NULL AND ir.quantidade_itens > 0
),
it_do AS (
  INSERT INTO elysium.movimentacoes_estoque_itens_producao (
    item_consumo_id, quantidade, data_movimentacao, lote, is_entrada,
    receita_id, is_ativo, descricao, preco_custo, lote_tag
  )
  SELECT
    i.item_producao_id,
    i.qtd,
    (SELECT data_mov_fim_dia FROM params),
    NULL,
    FALSE,
    (SELECT receita_id FROM params),
    NULL,
    'Consumo p/ receita ' || (SELECT op_tag FROM params),
    NULL,
    (SELECT op_tag FROM params)
  FROM it_rows i
  WHERE i.qtd > 0
  RETURNING id
),
prod AS (
  SELECT r.produto_id
  FROM elysium.receitas r
  JOIN params p ON p.receita_id = r.id
),
prod_in AS (
  INSERT INTO elysium.movimentacoes_estoque_produtos (
    produto_id, quantidade, tipo, operacao_id, data_mov, preco_venda
  )
  SELECT prod.produto_id, p.qtd_prod, 'entrada', 10, p.data_mov, p.preco_venda
  FROM prod, params p
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
    p.receita_id, pi.produto_id, p.data_mov,
    0, 0, 0, 0,
    pi.produto_estoque_id, p.qtd_prod, p.is_meia
  FROM params p
  JOIN prod_in pi ON TRUE
  RETURNING id
),
mp_out AS (
  SELECT
    s.materia_prima_id,
    s.quantidade_estoque AS qtd_estoque,
    e.quantidade_unidade AS qtd_por_unidade
  FROM elysium.movimentacoes_estoque_materia_prima s
  JOIN params p ON s.lote_tag = p.op_tag
  JOIN elysium.movimentacoes_estoque_materia_prima e
    ON e.is_entrada = TRUE
   AND e.materia_prima_id = s.materia_prima_id
   AND e.lote = s.lote
  WHERE s.is_entrada = FALSE
),
it_out AS (
  SELECT o.item_consumo_id, o.quantidade AS qtd
  FROM elysium.movimentacoes_estoque_itens_producao o
  JOIN params p ON o.lote_tag = p.op_tag
  WHERE o.is_entrada = FALSE
),
consumos AS (
  SELECT
    COALESCE(
      SUM(
        CASE
          WHEN COALESCE(mo.qtd_por_unidade, 0) > 1
            THEN mo.qtd_estoque / mo.qtd_por_unidade
          ELSE mo.qtd_estoque / 28.35
        END
      ), 0
    )::numeric(12,3) AS mp_qtd_consumida,
    COALESCE((SELECT SUM(qtd) FROM it_out), 0)::int AS it_qtd_consumida
  FROM mp_out mo
)
SELECT
  (SELECT id FROM rec_ins) AS rec_id,
  (SELECT produto_estoque_id FROM prod_in LIMIT 1) AS produto_mov_id,
  (SELECT mp_qtd_consumida FROM consumos) AS mp_qtd_consumida,
  (SELECT it_qtd_consumida FROM consumos) AS it_qtd_consumida,
  (SELECT op_tag FROM params) AS op_tag;
