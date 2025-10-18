SELECT
  mp.id                         AS materia_prima_id,
  mp.nome                       AS nome_materia_prima,
  mp.unidade_base,
  mp.medida_base,
  COALESCE(SUM(
    CASE WHEN m.is_entrada THEN m.quantidade_estoque ELSE -m.quantidade_estoque END
  ), 0)::numeric(12,3)          AS saldo_estoque,
  precos.preco_custo,
  MAX(m.data_mov)               AS data_movimentacao,
  proximo_lote.lote             AS lote
FROM elysium.materias_prima mp
LEFT JOIN elysium.movimentacoes_estoque_materia_prima m
  ON m.materia_prima_id = mp.id
 AND DATE(m.data_mov) <= :data_referencia
LEFT JOIN LATERAL (
  SELECT mm.preco_custo
  FROM elysium.movimentacoes_estoque_materia_prima mm
  WHERE mm.materia_prima_id = mp.id
    AND mm.preco_custo IS NOT NULL
    AND DATE(mm.data_mov) <= :data_referencia
  ORDER BY mm.data_mov DESC, mm.id DESC
  LIMIT 1
) AS precos ON TRUE
LEFT JOIN LATERAL (
  SELECT MIN(mm.lote) AS lote
  FROM elysium.movimentacoes_estoque_materia_prima mm
  WHERE mm.materia_prima_id = mp.id
    AND DATE(mm.data_mov) <= :data_referencia
    AND mm.is_entrada = TRUE
    AND mm.is_ativo = TRUE
) AS proximo_lote ON TRUE
GROUP BY mp.id, mp.nome, mp.unidade_base, mp.medida_base, precos.preco_custo, proximo_lote.lote
ORDER BY mp.nome;
