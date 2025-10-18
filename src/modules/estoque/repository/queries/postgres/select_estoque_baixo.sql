SELECT
    p.id   AS produto_id,
    p.nome AS nome_produto,
    COALESCE(SUM(
        CASE
            WHEN m.tipo = 'entrada' THEN m.quantidade
            WHEN m.tipo = 'saida'   THEN -m.quantidade
            ELSE 0
        END
    ), 0) AS saldo_estoque,
    p.estoque_minimo
FROM elysium.produtos p
LEFT JOIN elysium.movimentacoes_estoque_produtos m
       ON m.produto_id = p.id
      AND DATE(m.data_mov) <= :data_referencia
GROUP BY
    p.id, p.nome, p.estoque_minimo
HAVING
    COALESCE(SUM(
        CASE
            WHEN m.tipo = 'entrada' THEN m.quantidade
            WHEN m.tipo = 'saida'   THEN -m.quantidade
            ELSE 0
        END
    ), 0) < p.estoque_minimo
ORDER BY saldo_estoque ASC;
