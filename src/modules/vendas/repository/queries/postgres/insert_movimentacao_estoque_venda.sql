INSERT INTO ambrosia.movimentacoes_estoque (
  produto_id,
  quantidade,
  operacao_id,
  tipo,
  data_mov,
  venda_id
)
SELECT
  :produto_id,
  :quantidade,
  :operacao_id,
  tipo,
  :data_mov,
  COALESCE(CAST(:venda_id AS INTEGER), NULL)
FROM ambrosia.operacoes_estoque
WHERE id = :operacao_id
RETURNING id;
