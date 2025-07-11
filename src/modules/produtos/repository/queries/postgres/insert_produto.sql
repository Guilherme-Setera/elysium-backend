INSERT INTO ambrosia.produtos (nome, descricao, validade, ativo)
VALUES (:nome, :descricao, :validade, true)
RETURNING id;
