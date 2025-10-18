UPDATE elysium.usuarios
SET senha_hash = :senha_hash
WHERE id = :id
