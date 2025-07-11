INSERT INTO ambrosia.clientes (nome, celular, endereco, email, cpf, dt_start, ativo)
VALUES (:nome, :celular, :endereco, :email, :cpf, CURRENT_DATE, true)
RETURNING id;