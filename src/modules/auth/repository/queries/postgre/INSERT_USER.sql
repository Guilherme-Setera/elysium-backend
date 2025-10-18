INSERT INTO elysium.usuarios (nome, email, senha_hash, "role", ativo)
VALUES (%(nome)s, %(email)s, %(senha_hash)s, %(role)s, true)
RETURNING id