SELECT
  r.id,
  r.nome,
  r.descricao,
  r.produto_id,
  p.nome AS produto_nome,
  COALESCE(
    (
      SELECT json_agg(
               json_build_object(
                 'materia_prima_id',   mp.id,
                 'nome_materia_prima', mp.nome,
                 'quantidade',         ir.quantidade,
                 'unidade',            COALESCE(ir.unidade, mp.unidade_base)
               )
               ORDER BY mp.nome
             )
      FROM elysium.itens_receita ir
      JOIN elysium.materias_prima mp ON mp.id = ir.materia_prima_id
      WHERE ir.receita_id = r.id
    ),
    '[]'::json
  ) AS materias_primas,
  COALESCE(
    (
      SELECT json_agg(
               json_build_object(
                 'item_producao_id', ip.id,
                 'nome_item',        ip.nome,
                 'quantidade_itens', ir.quantidade_itens,
                 'unidade',          COALESCE(ir.unidade, 'un')
               )
               ORDER BY ip.nome
             )
      FROM elysium.itens_receita ir
      JOIN elysium.itens_producao ip ON ip.id = ir.item_producao_id
      WHERE ir.receita_id = r.id
    ),
    '[]'::json
  ) AS itens_producao
FROM elysium.receitas r
JOIN elysium.produtos p ON p.id = r.produto_id
WHERE (:receita_id IS NULL OR r.id = :receita_id)
  AND (:produto_id IS NULL OR r.produto_id = :produto_id)
ORDER BY r.nome;
