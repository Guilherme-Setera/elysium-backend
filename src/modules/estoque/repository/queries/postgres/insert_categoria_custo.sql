INSERT INTO ambrosia.categorias_custo (
    nome
)
VALUES (
    :nome
)
RETURNING id;
