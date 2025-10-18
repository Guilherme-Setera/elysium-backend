SELECT 
  mp.nome,
  mpp.preco_custo,

  COALESCE((
    SELECT SUM(CASE WHEN me.tipo = 'entrada' THEN me.quantidade_unidade
                    WHEN me.tipo = 'saida'   THEN -me.quantidade_unidade
                    ELSE 0 END)
    FROM elysium.movimentacoes_estoque_materia_prima me
    WHERE me.materia_prima_id = mpp.materia_prima_id
      AND me.data_mov <= :data_base
  ), 0) AS estoque_unidade,

  COALESCE((
    SELECT SUM(CASE WHEN me.tipo = 'entrada' THEN me.quantidade_medida
                    WHEN me.tipo = 'saida'   THEN -me.quantidade_medida
                    ELSE 0 END)
    FROM elysium.movimentacoes_estoque_materia_prima me
    WHERE me.materia_prima_id = mpp.materia_prima_id
      AND me.data_mov <= :data_base
  ), 0) AS estoque_medida

FROM elysium.materia_prima_precos mpp
JOIN elysium.materias_prima mp ON mp.id = mpp.materia_prima_id
WHERE mpp.materia_prima_id = :materia_prima_id
  AND mpp.data_referencia <= :data_base
  AND (mpp.data_fim IS NULL OR mpp.data_fim >= :data_base)
ORDER BY mpp.data_referencia DESC
LIMIT 1;
