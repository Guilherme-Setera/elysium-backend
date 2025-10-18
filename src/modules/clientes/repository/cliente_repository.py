import os
from typing import Optional, cast
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.engine import CursorResult
from src.modules.clientes.dto.dto import ClienteResponse, ClienteCreate
from src.modules.clientes.abc_classes.clientes_abc import IClienteRepository

BASE_DIR: str = os.path.dirname(__file__)
QUERIES_FOLDER: str = os.path.join(BASE_DIR, "queries", "postgres")


class ClienteRepository(IClienteRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def cadastrar_cliente(self, cliente: ClienteCreate) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_cliente.sql")
        query: str = open(query_path).read()

        result = self.session.execute(text(query), {
            "nome": cliente.nome,
            "celular": cliente.celular,
            "endereco": cliente.endereco,
            "email": cliente.email,
            "cpf": cliente.cpf,
            "descricao": cliente.descricao,
        }).fetchone()

        self.session.commit()
        return result[0] if result else -1
    
    def cadastrar_clientes_em_lote(self, clientes: list[ClienteCreate]) -> list[int]:
        if not clientes:
            return []
        values = []
        params = {}
        for idx, c in enumerate(clientes):
            values.append(
                f"(:nome{idx}, :celular{idx}, :endereco{idx}, :email{idx}, :cpf{idx}, :descricao{idx})"
            )
            params[f'nome{idx}'] = c.nome
            params[f'celular{idx}'] = c.celular
            params[f'endereco{idx}'] = c.endereco
            params[f'email{idx}'] = c.email
            params[f'cpf{idx}'] = c.cpf
            params[f'descricao{idx}'] = c.descricao

        query = f"""
        INSERT INTO elysium.clientes (nome, celular, endereco, email, cpf, descricao)
        VALUES {', '.join(values)}
        RETURNING id;
        """
        result = self.session.execute(text(query), params)
        ids = [row[0] for row in result.fetchall()]
        self.session.commit()
        return ids

    def atualizar_cliente(
        self,
        cliente_id: int,
        nome: str,
        celular: str,
        endereco: Optional[str],
        email: Optional[str],
        cpf: Optional[str],
        descricao: Optional[str]
    ) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "update_cliente.sql")
        query: str = open(query_path).read()

        result = cast(CursorResult, self.session.execute(text(query), {
            "id": cliente_id,
            "nome": nome,
            "celular": celular,
            "endereco": endereco,
            "email": email,
            "cpf": cpf,
            "descricao": descricao,
        }))

        self.session.commit()
        return result.rowcount

    def desativar_cliente(self, cliente_id: int) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "desativar_cliente.sql")
        query: str = open(query_path).read()

        result = cast(CursorResult, self.session.execute(text(query), {"id": cliente_id}))

        self.session.commit()
        return result.rowcount

    def listar_clientes_ativos(self) -> list[ClienteResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_clientes_ativos.sql")
        query: str = open(query_path).read()

        rows = self.session.execute(text(query)).fetchall()

        return [
            ClienteResponse(
                id=row[0],
                nome=row[1],
                celular=row[2],
                endereco=row[3],
                email=row[4],
                cpf=row[5],
                descricao=row[6],
                dt_start=row[7]
            )
            for row in rows
        ]
