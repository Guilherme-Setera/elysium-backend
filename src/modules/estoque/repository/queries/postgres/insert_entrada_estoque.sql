INSERT INTO ambrosia.movimentacoes_estoque (
    produto_id,
    tipo,
    quantidade,
    operacao_id
) VALUES (
    :produto_id,
    'entrada',
    :quantidade,
    :operacao_id
)
RETURNING id;
