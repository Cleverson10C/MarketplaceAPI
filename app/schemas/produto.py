from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.types import StringConstraints


class ProdutoBase(BaseModel):
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    preco: float = Field(gt=0)


class ProdutoCriacao(ProdutoBase):
    quantidade: int = Field(ge=0)
    estoque_minimo: int = Field(ge=0, default=0)


class ProdutoAtualizacao(BaseModel):
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    preco: float = Field(gt=0)
    estoque_minimo: int = Field(ge=0, default=0)


class ProdutoResposta(BaseModel):
    id: int
    nome: str
    preco: float
    estoque: int
    estoque_minimo: int

    class Config:
        from_attributes = True


class MovimentoEstoqueCriacao(BaseModel):
    tipo: str = Field(pattern="^(entrada|saida|ajuste)$")
    quantidade: int = Field(gt=0)


class MovimentoEstoqueResposta(BaseModel):
    id: int
    produto_id: int
    tipo: str
    quantidade: int
    estoque_antes: int
    estoque_depois: int
    criado_em: datetime

    class Config:
        from_attributes = True


class RastreamentoProdutoCriacao(BaseModel):
    status: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    localizacao: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    observacao: str | None = Field(default=None, max_length=500)


class RastreamentoProdutoResposta(BaseModel):
    id: int
    produto_id: int
    status: str
    localizacao: str
    observacao: str | None
    criado_em: datetime

    class Config:
        from_attributes = True
