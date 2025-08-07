SELECT 
  id,
  nome,
  celular,
  endereco,
  email,
  cpf,
  descricao,
  dt_start
FROM ambrosia.clientes
WHERE ativo = true
ORDER BY nome;
