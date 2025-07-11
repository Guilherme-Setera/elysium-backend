UPDATE ambrosia.produtos
SET nome = :nome,
    descricao = :descricao,
    validade = :validade
WHERE id = :id;
