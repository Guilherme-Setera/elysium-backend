INSERT INTO elysium.materias_prima (
  nome,
  descricao,
  estoque_minimo,
  medida_base,
  is_grama,
  is_ml
) VALUES (
  :nome,
  :descricao,
  COALESCE(:estoque_minimo_unidade, :estoque_minimo, 0),
  COALESCE(:medida_base, 1),
  CASE
    WHEN :unidade = 'g'  THEN TRUE
    WHEN :unidade = 'ml' THEN FALSE
    ELSE COALESCE(:is_grama, TRUE)
  END,
  CASE
    WHEN :unidade = 'g'  THEN FALSE
    WHEN :unidade = 'ml' THEN TRUE
    ELSE NOT COALESCE(:is_grama, TRUE)
  END
)
RETURNING id;
