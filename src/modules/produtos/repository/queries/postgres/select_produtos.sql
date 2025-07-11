SELECT
    p.id,
    p.nome,
    p.descricao,
    p.validade,
    p.ativo,
    pp.preco_custo,
    pp.preco_venda,
    pp.data_referencia AS data_preco
FROM
    ambrosia.produtos p
LEFT JOIN LATERAL (
    SELECT
        preco_custo,
        preco_venda,
        data_referencia
    FROM ambrosia.produtos_precos pp
    WHERE pp.produto_id = p.id AND pp.data_referencia <= :data_referencia
    ORDER BY pp.data_referencia DESC
    LIMIT 1
) pp ON TRUE
ORDER BY p.id DESC;
