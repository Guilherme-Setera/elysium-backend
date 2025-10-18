UPDATE elysium.itens_producao
SET ativo = FALSE
WHERE id = :id
  AND ativo = TRUE
RETURNING id;