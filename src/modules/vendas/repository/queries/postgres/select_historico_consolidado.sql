-- select_historico_consolidado.sql
-- Retorna histórico consolidado de vendas com custos, lucros e detalhes
WITH vendas_filtradas AS (
  SELECT
    v.id,
    v.cliente_id,
    v.data_venda,
    v.total,
    v.valor_pago,
    v.status,
    v.pago,
    -- Para a_prazo, usa a data do último pagamento como data_quitacao
    CASE
      WHEN v.a_prazo AND v.pago THEN (
        SELECT MAX(p.data_pagamento)
        FROM elysium.venda_parcelas p
        WHERE p.venda_id = v.id AND p.data_pagamento IS NOT NULL
      )
      WHEN NOT v.a_prazo AND v.pago THEN v.data_pagamento
      ELSE NULL
    END AS data_quitacao
  FROM elysium.vendas v
  WHERE v.cancelada = FALSE
    AND (:data_de IS NULL OR
      CASE
        WHEN :usar_data = 'data_venda' THEN DATE(v.data_venda) >= :data_de
        WHEN :usar_data = 'data_quitacao' THEN (
          CASE
            WHEN v.a_prazo AND v.pago THEN (
              SELECT MAX(p.data_pagamento)
              FROM elysium.venda_parcelas p
              WHERE p.venda_id = v.id AND p.data_pagamento IS NOT NULL
            )
            WHEN NOT v.a_prazo AND v.pago THEN DATE(v.data_pagamento)
            ELSE NULL
          END
        ) >= :data_de
        ELSE TRUE
      END
    )
    AND (:data_ate IS NULL OR
      CASE
        WHEN :usar_data = 'data_venda' THEN DATE(v.data_venda) <= :data_ate
        WHEN :usar_data = 'data_quitacao' THEN (
          CASE
            WHEN v.a_prazo AND v.pago THEN (
              SELECT MAX(p.data_pagamento)
              FROM elysium.venda_parcelas p
              WHERE p.venda_id = v.id AND p.data_pagamento IS NOT NULL
            )
            WHEN NOT v.a_prazo AND v.pago THEN DATE(v.data_pagamento)
            ELSE NULL
          END
        ) <= :data_ate
        ELSE TRUE
      END
    )
),
itens_com_custo AS (
  SELECT
    iv.venda_id,
    iv.produto_id,
    p.nome AS produto_nome,
    iv.quantidade,
    iv.preco_unitario,
    iv.subtotal AS valor_venda,
    -- Buscar o preço de custo da entrada mais recente antes da venda
    COALESCE((
      SELECT m.preco_custo
      FROM elysium.movimentacoes_estoque_produtos m
      WHERE m.produto_id = iv.produto_id
        AND m.tipo = 'entrada'
        AND m.preco_custo IS NOT NULL
        AND m.data_mov <= (SELECT data_venda FROM vendas_filtradas WHERE id = iv.venda_id)
      ORDER BY m.data_mov DESC, m.id DESC
      LIMIT 1
    ), 0) AS preco_custo_unitario,
    COALESCE((
      SELECT m.preco_custo
      FROM elysium.movimentacoes_estoque_produtos m
      WHERE m.produto_id = iv.produto_id
        AND m.tipo = 'entrada'
        AND m.preco_custo IS NOT NULL
        AND m.data_mov <= (SELECT data_venda FROM vendas_filtradas WHERE id = iv.venda_id)
      ORDER BY m.data_mov DESC, m.id DESC
      LIMIT 1
    ), 0) * iv.quantidade AS custo_total
  FROM elysium.itens_venda iv
  INNER JOIN elysium.produtos p ON p.id = iv.produto_id
  WHERE iv.venda_id IN (SELECT id FROM vendas_filtradas)
),
receitas_produtos AS (
  SELECT
    icc.venda_id,
    icc.produto_id,
    r.id AS receita_id,
    r.nome AS receita_nome,
    -- Custos de matérias-primas
    json_agg(
      DISTINCT jsonb_build_object(
        'nome', mp.nome,
        'quantidade', ir.quantidade * icc.quantidade,
        'unidade', ir.unidade,
        'valor', COALESCE((
          SELECT mmp.preco_custo * (ir.quantidade * icc.quantidade)
          FROM elysium.movimentacoes_estoque_materia_prima mmp
          WHERE mmp.materia_prima_id = ir.materia_prima_id
            AND mmp.is_entrada = true
            AND mmp.preco_custo IS NOT NULL
            AND mmp.data_mov <= (SELECT data_venda FROM vendas_filtradas WHERE id = icc.venda_id)
          ORDER BY mmp.data_mov DESC, mmp.id DESC
          LIMIT 1
        ), 0)
      )
    ) FILTER (WHERE ir.materia_prima_id IS NOT NULL) AS materias_primas,
    -- Custos de itens de produção
    json_agg(
      DISTINCT jsonb_build_object(
        'nome', ip.nome,
        'quantidade', ir.quantidade_itens * icc.quantidade,
        'valor', COALESCE((
          SELECT mip.preco_custo * (ir.quantidade_itens * icc.quantidade)
          FROM elysium.movimentacoes_estoque_itens_producao mip
          WHERE mip.item_consumo_id = ir.item_producao_id
            AND mip.is_entrada = true
            AND mip.preco_custo IS NOT NULL
            AND mip.data_movimentacao <= (SELECT data_venda FROM vendas_filtradas WHERE id = icc.venda_id)
          ORDER BY mip.data_movimentacao DESC, mip.id DESC
          LIMIT 1
        ), 0)
      )
    ) FILTER (WHERE ir.item_producao_id IS NOT NULL) AS itens_producao_componentes
  FROM itens_com_custo icc
  INNER JOIN elysium.receitas r ON r.produto_id = icc.produto_id
  INNER JOIN elysium.itens_receita ir ON ir.receita_id = r.id
  LEFT JOIN elysium.materias_prima mp ON mp.id = ir.materia_prima_id
  LEFT JOIN elysium.itens_producao ip ON ip.id = ir.item_producao_id
  GROUP BY icc.venda_id, icc.produto_id, r.id, r.nome
)
SELECT
  vf.id,
  vf.id AS venda_id,
  c.nome AS cliente_nome,
  vf.data_venda,
  vf.data_quitacao,
  vf.total AS valor_total,
  vf.valor_pago,
  COALESCE(SUM(icc.custo_total), 0) AS valor_custo,
  vf.valor_pago - COALESCE(SUM(icc.custo_total), 0) AS lucro,
  -- Agregação de matérias-primas por venda (de todas as receitas)
  (
    SELECT json_agg(mp_agg)
    FROM (
      SELECT
        mp_item->>'nome' AS nome,
        SUM((mp_item->>'quantidade')::numeric) AS quantidade,
        mp_item->>'unidade' AS unidade,
        SUM((mp_item->>'valor')::numeric) AS valor
      FROM receitas_produtos rp
      CROSS JOIN json_array_elements(rp.materias_primas) AS mp_item
      WHERE rp.venda_id = vf.id
      GROUP BY mp_item->>'nome', mp_item->>'unidade'
    ) AS mp_agg
  ) AS materias_primas,
  -- Agregação de itens de produção vendidos
  json_agg(
    json_build_object(
      'nome', icc.produto_nome,
      'quantidade', icc.quantidade,
      'valor', icc.valor_venda
    )
  ) AS itens_producao,
  NOW() AS created_at,
  NOW() AS updated_at
FROM vendas_filtradas vf
LEFT JOIN elysium.clientes c ON c.id = vf.cliente_id
LEFT JOIN itens_com_custo icc ON icc.venda_id = vf.id
GROUP BY vf.id, vf.data_venda, vf.data_quitacao, vf.total, vf.valor_pago, c.nome
ORDER BY
  CASE
    WHEN :usar_data = 'data_quitacao' THEN vf.data_quitacao
    ELSE vf.data_venda
  END DESC,
  vf.id DESC;
