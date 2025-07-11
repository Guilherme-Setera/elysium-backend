from pydantic import BaseModel


class MovimentacaoCreate(BaseModel):
    produto_id: int
    quantidade: int
    operacao_id: int | None = None


class EstoqueAtualResponse(BaseModel):
    produto_id: int
    nome_produto: str
    saldo_estoque: int


class EstoqueBaixoResponse(BaseModel):
    produto_id: int
    nome_produto: str
    saldo_estoque: int
    estoque_minimo: int

class OperacaoResponse(BaseModel):
    id: int
    descricao: str
    tipo: str 