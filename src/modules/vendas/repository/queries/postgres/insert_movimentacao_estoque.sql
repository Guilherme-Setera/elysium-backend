-- insert_movimentacao_estoque.sql
INSERT INTO ambrosia.movimentacoes_estoque (
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
FROM ambrosia.operacoes_estoque
WHERE id = :operacao_id
RETURNING id;
