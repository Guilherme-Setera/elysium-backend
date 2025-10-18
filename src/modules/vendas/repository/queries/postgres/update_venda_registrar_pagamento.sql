UPDATE elysium.vendas
SET valor_pago = COALESCE(valor_pago,0) + :valor_recebido
WHERE id = :venda_id;