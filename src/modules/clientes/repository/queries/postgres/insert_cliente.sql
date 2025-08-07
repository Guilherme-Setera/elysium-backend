INSERT INTO ambrosia.clientes (
  nome,
  celular,
  endereco,
  email,
  cpf,
  descricao,
  dt_start,
  ativo
)
VALUES (
  :nome,
  :celular,
  :endereco,
  :email,
  :cpf,
  :descricao,
  CURRENT_DATE,
  true
)
RETURNING id;
