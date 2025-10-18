SELECT
  email AS str_Login,
  senha_hash AS str_PwdHash,
  nome AS str_Nome,
  "role" AS str_Role,
  COALESCE(totp_secret, '') AS str_TotpSecret,
  COALESCE(totp_enabled, false) AS bln_TotpEnabled,
  COALESCE(totp_last_interval, 0) AS num_TotpLastInterval
FROM elysium.usuarios
WHERE ativo = TRUE
