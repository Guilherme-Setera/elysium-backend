DELETE FROM ambrosia.movimentacoes_estoque
WHERE operacao_id IN (5, 7)
AND venda_id = :venda_id