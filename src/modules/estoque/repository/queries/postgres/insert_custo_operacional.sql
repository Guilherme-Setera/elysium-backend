INSERT INTO ambrosia.custos_operacionais (
    categoria,
    valor,
    data_referencia,
    observacao
)
VALUES (
    :categoria,
    :valor,
    :data_referencia,
    :observacao
)
RETURNING id;