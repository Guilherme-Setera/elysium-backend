SELECT id, categoria, valor, data_referencia, observacao
FROM ambrosia.custos_operacionais
WHERE data_referencia BETWEEN :data_inicio AND :data_fim
ORDER BY data_referencia DESC;
