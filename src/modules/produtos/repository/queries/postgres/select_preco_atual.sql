SELECT preco_custo, preco_venda
FROM elysium.produtos_precos
WHERE produto_id = :produto_id AND data_referencia <= :data_base
ORDER BY data_referencia DESC
LIMIT 1;
