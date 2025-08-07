INSERT INTO ambrosia.custos_operacionais (
    categoria_id,
    valor,
    data_referencia,
    observacao
)
VALUES (
    :categoria_id,
    :valor,
    :data_referencia,
    :observacao
)
RETURNING id;
