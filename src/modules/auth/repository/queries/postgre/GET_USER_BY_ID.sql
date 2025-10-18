SELECT
  id,
  email AS login,
  senha_hash,
  nome,
  "role",
  ativo,
  COALESCE(totp_secret, '') AS totp_secret,
  COALESCE(totp_enabled, false) AS totp_enabled,
  COALESCE(totp_last_interval, 0) AS totp_last_interval
FROM elysium.usuarios
WHERE id = %(id)s
LIMIT 1