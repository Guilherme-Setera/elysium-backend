UPDATE elysium.movimentacoes_receitas
SET
  custo_materia_prima  = COALESCE(CAST(:custo_mp AS numeric(12,4)), custo_materia_prima),
  custo_itens_producao = COALESCE(CAST(:custo_it AS numeric(12,4)), custo_itens_producao)
WHERE id = :rec_id;