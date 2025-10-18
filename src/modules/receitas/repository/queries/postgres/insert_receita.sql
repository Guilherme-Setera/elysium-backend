WITH nova_receita AS (
  INSERT INTO elysium.receitas (produto_id, nome, descricao)
  VALUES (:produto_id, :nome, :descricao)
  RETURNING id
),
itens AS (
  SELECT
    i.materia_prima_id::int AS materia_prima_id,
    i.item_producao_id::int AS item_producao_id,
    i.quantidade::numeric   AS quantidade,
    i.quantidade_itens::int AS quantidade_itens
  FROM jsonb_to_recordset(CAST(:itens AS jsonb)) AS i(
    materia_prima_id int,
    item_producao_id int,
    quantidade numeric,
    quantidade_itens int
  )
),
ins AS (
  INSERT INTO elysium.itens_receita
    (receita_id, materia_prima_id, item_producao_id, quantidade, quantidade_itens)
  SELECT nr.id, it.materia_prima_id, it.item_producao_id, it.quantidade, it.quantidade_itens
  FROM nova_receita nr
  JOIN itens it ON TRUE
  RETURNING 1
)
SELECT id AS receita_id
FROM nova_receita;
