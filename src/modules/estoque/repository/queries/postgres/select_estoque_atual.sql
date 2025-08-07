SELECT
    p.id AS produto_id,
    p.nome AS nome_produto,
    SUM(
        CASE 
            WHEN m.tipo = 'entrada' THEN m.quantidade
            WHEN m.tipo = 'saida' THEN -m.quantidade
            ELSE 0
        END
    ) AS saldo_estoque,
    precos.preco_custo,
    precos.preco_venda,
    MAX(m.data_mov) AS data_movimentacao
FROM ambrosia.produtos p
INNER JOIN ambrosia.movimentacoes_estoque m
    ON m.produto_id = p.id
    AND DATE(m.data_mov) <= :data_referencia
LEFT JOIN LATERAL (
    SELECT pp.preco_custo, pp.preco_venda
    FROM ambrosia.produtos_precos pp
    WHERE pp.produto_id = p.id
      AND pp.data_referencia <= :data_referencia
      AND pp.data_fim IS NULL
    ORDER BY pp.data_referencia DESC
    LIMIT 1
) AS precos ON true
GROUP BY p.id, p.nome, precos.preco_custo, precos.preco_venda
ORDER BY p.nome;
