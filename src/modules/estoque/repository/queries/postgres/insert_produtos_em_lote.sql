INSERT INTO elysium.produtos (
    nome,
    descricao,
    validade,
    ativo,
    estoque_minimo
)
VALUES
    {valores}
RETURNING id;
