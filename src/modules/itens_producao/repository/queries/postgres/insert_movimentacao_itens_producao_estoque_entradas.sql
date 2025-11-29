WITH proximo_lote AS (
    SELECT COALESCE(MAX(lote) + 1, 1) AS lote
    FROM elysium.movimentacoes_estoque_itens_producao
    WHERE item_consumo_id = :item_consumo_id
      AND is_entrada = TRUE
)
INSERT INTO elysium.movimentacoes_estoque_itens_producao (
    item_consumo_id,
    quantidade,
    preco_custo,
    data_movimentacao,
    lote,
    is_entrada,
    is_ativo,
    descricao
)
SELECT
    :item_consumo_id,
    :quantidade,
    :preco_custo,
    COALESCE(:data_movimentacao, CURRENT_TIMESTAMP),
    (SELECT lote FROM proximo_lote),
    TRUE,
    COALESCE(:is_ativo, TRUE),
    :descricao
RETURNING id;
