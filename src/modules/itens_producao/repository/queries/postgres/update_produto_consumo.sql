UPDATE elysium.itens_producao
SET
  nome = COALESCE(NULLIF(TRIM(:nome), ''), nome),
  ativo = COALESCE(:ativo, ativo),
  estoque_minimo = CASE
    WHEN :limpar_estoque_minimo IS TRUE THEN NULL
    WHEN :estoque_minimo IS NOT NULL THEN :estoque_minimo
    ELSE estoque_minimo
  END
WHERE id = :item_consumo_id
RETURNING id, nome, ativo, estoque_minimo;