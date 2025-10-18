INSERT INTO elysium.movimentacoes_estoque_materia_prima (
  materia_prima_id,
  quantidade_estoque,
  data_mov,
  operacao_id,
  quantidade_unidade,
  preco_custo,
  is_entrada,
  is_ativo
)
SELECT
  :materia_prima_id,
  (:quantidade_unidade * mp.medida_base)::numeric,
  COALESCE(:data_mov, CURRENT_TIMESTAMP),
  :operacao_id,
  :quantidade_unidade,
  :preco_custo,
  CASE WHEN oe.tipo = 'entrada' THEN TRUE ELSE FALSE END,
  TRUE
FROM elysium.operacoes_estoque oe
JOIN elysium.materias_prima mp ON mp.id = :materia_prima_id
WHERE oe.id = :operacao_id
  AND oe.is_materia_prima = TRUE
RETURNING id;