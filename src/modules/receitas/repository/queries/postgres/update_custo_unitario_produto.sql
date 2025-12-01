UPDATE elysium.movimentacoes_receitas
SET custo_unitario_produto = CASE
  WHEN quantidade_produto > 0 THEN custo_total_producao / quantidade_produto
  ELSE NULL
END
WHERE id = :rec_id;
