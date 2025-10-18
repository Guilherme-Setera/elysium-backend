INSERT INTO elysium.categorias_custo (
    nome
)
VALUES (
    :nome
)
RETURNING id;
