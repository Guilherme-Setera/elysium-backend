SELECT
  id,
  nome,
  descricao,
  ativo,
  estoque_minimo,
  medida_base,
  unidade_base,
  densidade
FROM elysium.materias_prima
ORDER BY nome;