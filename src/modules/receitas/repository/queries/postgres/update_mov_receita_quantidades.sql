UPDATE elysium.movimentacoes_receitas
SET
  quantidade_materia_prima   = :mp_qtd,
  quantidade_itens_producao  = :it_qtd
WHERE id = :rec_id;
