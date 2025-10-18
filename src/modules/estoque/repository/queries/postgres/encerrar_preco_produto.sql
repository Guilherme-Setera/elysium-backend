UPDATE elysium.produtos_precos
SET data_fim = CURRENT_DATE
WHERE produto_id = :id AND data_fim IS NULL;