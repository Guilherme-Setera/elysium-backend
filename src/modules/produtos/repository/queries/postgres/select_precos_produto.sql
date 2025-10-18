SELECT id, produto_id, data_referencia, preco_custo, preco_venda
FROM elysium.produtos_precos
WHERE produto_id = :produto_id
ORDER BY data_referencia DESC;
