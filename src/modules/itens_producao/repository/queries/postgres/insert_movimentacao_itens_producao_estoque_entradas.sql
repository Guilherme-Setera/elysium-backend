INSERT INTO elysium.movimentacoes_estoque_itens_producao (
  item_consumo_id,
  quantidade,
  preco_custo,
  data_movimentacao,
  is_entrada,
  is_ativo,
  descricao
)
VALUES (
  :item_consumo_id,
  :quantidade,
  :preco_custo,
  COALESCE(:data_movimentacao, CURRENT_TIMESTAMP),
  TRUE,
  COALESCE(:is_ativo, TRUE),
  :descricao
)
RETURNING id;
