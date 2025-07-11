INSERT INTO ambrosia.log_alteracoes_vendas (
  venda_id,
  campo_alterado,
  valor_anterior,
  valor_novo,
  usuario_responsavel,
  data_alteracao
)
VALUES (
  :venda_id,
  :campo_alterado,
  :valor_anterior,
  :valor_novo,
  :usuario_responsavel,
  CURRENT_TIMESTAMP
);
