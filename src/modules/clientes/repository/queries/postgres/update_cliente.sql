UPDATE ambrosia.clientes
SET nome = :nome,
    celular = :celular,
    endereco = :endereco,
    email = :email,
    cpf = :cpf,
    descricao = :descricao
WHERE id = :id AND ativo = true;