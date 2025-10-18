INSERT INTO elysium.produtos (
  nome,
  descricao,
  meses_para_vencer,
  ativo,
  estoque_minimo
)
VALUES (
  :nome,
  :descricao,
  :meses_para_vencer,
  :ativo,
  :estoque_minimo
)
RETURNING id;
