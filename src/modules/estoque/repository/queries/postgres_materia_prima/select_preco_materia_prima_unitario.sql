SELECT 
  id, 
  materia_prima_id, 
  data_referencia, 
  preco_custo, 
  data_fim
FROM elysium.materia_prima_precos
WHERE materia_prima_id = :materia_prima_id
ORDER BY data_referencia DESC;