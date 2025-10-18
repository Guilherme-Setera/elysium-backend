SELECT
  co.id,
  co.categoria_id,
  cc.nome AS nome_categoria,
  co.valor,
  co.data_referencia,
  co.observacao
FROM elysium.custos_operacionais co
JOIN elysium.categorias_custo cc ON co.categoria_id = cc.id
WHERE co.data_referencia BETWEEN :data_inicio AND :data_fim
ORDER BY co.data_referencia DESC;
