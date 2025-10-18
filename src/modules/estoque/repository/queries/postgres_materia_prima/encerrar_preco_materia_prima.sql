UPDATE elysium.materia_prima_precos
SET data_fim = CURRENT_DATE
WHERE materia_prima_id = :id
  AND data_fim IS NULL;
