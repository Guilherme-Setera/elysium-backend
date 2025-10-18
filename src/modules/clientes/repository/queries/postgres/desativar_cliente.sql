UPDATE elysium.clientes
SET ativo = false,
    dt_end = CURRENT_DATE
WHERE id = :id AND ativo = true;