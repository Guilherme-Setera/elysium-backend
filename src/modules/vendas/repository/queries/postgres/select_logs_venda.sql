SELECT 
  l.id,
  l.venda_id,
  l.campo_alterado,
  l.valor_anterior,
  l.valor_novo,
  l.usuario_responsavel,
  l.data_alteracao
FROM ambrosia.log_alteracoes_vendas l
WHERE 
  (:venda_id IS NULL OR l.venda_id = :venda_id)
  AND (:data_inicio IS NULL OR l.data_alteracao >= :data_inicio)
  AND (:data_fim IS NULL OR l.data_alteracao <= :data_fim)
ORDER BY l.data_alteracao DESC;
