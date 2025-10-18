SELECT
    m.id,
    m.item_consumo_id,
    i.nome AS nome_item,
    m.quantidade,
    m.preco_custo,
    m.data_movimentacao,
    m.lote,
    m.is_entrada,
    CASE WHEN m.is_entrada THEN 'entrada' ELSE 'saida' END AS tipo_movimentacao,
    m.receita_id,
    r.nome AS nome_receita,
    m.is_ativo,
    m.descricao
FROM elysium.movimentacoes_estoque_itens_producao m
JOIN elysium.itens_producao i ON i.id = m.item_consumo_id
LEFT JOIN elysium.receitas r ON r.id = m.receita_id
WHERE m.data_movimentacao < (CAST(:dia_limite AS date) + INTERVAL '1 day')
ORDER BY m.data_movimentacao DESC, m.id DESC;
