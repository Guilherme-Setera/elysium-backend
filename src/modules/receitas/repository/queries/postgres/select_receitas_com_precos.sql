SELECT
    mr.id,
    mr.receita_id,
    r.nome              AS receita_nome,
    mr.produto_id,
    p.nome              AS produto_nome,
    mr.data_execucao,
    mr.quantidade_materia_prima,
    mr.custo_materia_prima,
    mr.quantidade_itens_producao,
    mr.custo_itens_producao,
    mr.produto_estoque_id,
    mr.quantidade_produto,
    mr.is_meia_receita,
    mr.custo_total_producao,
    mr.custo_unitario_produto
FROM elysium.movimentacoes_receitas mr
JOIN elysium.receitas r
  ON r.id = mr.receita_id
JOIN elysium.produtos p
  ON p.id = mr.produto_id
WHERE (:receita_id IS NULL OR mr.receita_id = :receita_id)
  AND (:produto_id IS NULL OR mr.produto_id = :produto_id)
  AND (:data_inicio IS NULL OR mr.data_execucao >= :data_inicio)
  AND (:data_fim IS NULL OR mr.data_execucao <= :data_fim)
ORDER BY mr.data_execucao DESC, mr.id DESC;
