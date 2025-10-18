WITH p AS (
  SELECT
    CAST(:materia_prima_id AS int)                AS id,
    CAST(NULLIF(:nome, '') AS text)               AS nome,
    CAST(NULLIF(:descricao, '') AS text)          AS descricao,
    CAST(:ativo AS boolean)                       AS ativo,
    CAST(:estoque_minimo_unidade AS numeric)      AS estoque_minimo,
    CAST(:medida_base AS numeric)                 AS medida_base,
    CAST(:unidade AS text)                        AS unidade,
    CAST(:is_grama AS boolean)                    AS is_g,
    CAST(:is_ml AS boolean)                       AS is_m
)
UPDATE elysium.materias_prima m
SET
  nome           = COALESCE(p.nome, m.nome),
  descricao      = COALESCE(p.descricao, m.descricao),
  ativo          = COALESCE(p.ativo, m.ativo),
  estoque_minimo = COALESCE(p.estoque_minimo, m.estoque_minimo),
  medida_base    = COALESCE(p.medida_base, m.medida_base),
  is_grama       = COALESCE(
                     CASE
                       WHEN p.unidade = 'g'  THEN TRUE
                       WHEN p.unidade = 'ml' THEN FALSE
                       WHEN p.is_g IS NOT NULL THEN p.is_g
                       WHEN p.is_m IS NOT NULL THEN NOT p.is_m
                       ELSE NULL
                     END,
                     m.is_grama
                   ),
  is_ml          = COALESCE(
                     CASE
                       WHEN p.unidade = 'ml' THEN TRUE
                       WHEN p.unidade = 'g'  THEN FALSE
                       WHEN p.is_m IS NOT NULL THEN p.is_m
                       WHEN p.is_g IS NOT NULL THEN NOT p.is_g
                       ELSE NULL
                     END,
                     m.is_ml
                   )
FROM p
WHERE m.id = p.id
RETURNING m.id;
