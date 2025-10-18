-- queries/postgres/insert_movimentacao_estoque_venda.sql
INSERT INTO elysium.movimentacoes_estoque_produtos (
  produto_id,
  quantidade,
  operacao_id,
  tipo,
  data_mov,
  venda_id,
  lote_numero,
  data_validade,
  preco_custo,
  preco_venda
)
SELECT
  :produto_id,
  :quantidade,
  :operacao_id,
  oe.tipo,
  COALESCE(:data_mov, CURRENT_TIMESTAMP),
  COALESCE(CAST(:venda_id AS INTEGER), NULL),
  NULL,
  NULL,
  NULL,
  NULL
FROM elysium.operacoes_estoque oe
WHERE oe.id = :operacao_id
  AND oe.tipo IN ('saida','entrada')
RETURNING id;
