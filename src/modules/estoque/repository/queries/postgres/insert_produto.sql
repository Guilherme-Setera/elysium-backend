INSERT INTO ambrosia.produtos (
    nome,
    descricao,
    validade,
    ativo,
    estoque_minimo
)
VALUES (
    :nome,
    :descricao,
    :validade,
    :ativo,
    :estoque_minimo
)
RETURNING id;