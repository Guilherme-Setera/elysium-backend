INSERT INTO elysium.movimentacoes_estoque (
  produto_id,
  quantidade,
  operacao_id,
  tipo,
  data_mov
)
SELECT
  :produto_id,
  :quantidade,
  :operacao_id,
  tipo,
  :data_mov
FROM elysium.operacoes_estoque
WHERE id = :operacao_id
RETURNING id;