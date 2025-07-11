SELECT 
    email AS str_Login,
    senha_hash AS str_PwdHash,
    "role" AS str_Role
FROM ambrosia.usuarios
WHERE ativo = TRUE
