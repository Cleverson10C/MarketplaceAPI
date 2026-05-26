from pydantic import BaseModel, Field

class ItemPedidoCriar(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)

class PedidoCriar(BaseModel):
    itens: list[ItemPedidoCriar]

class PedidoResposta(BaseModel):
    id: int
    total: float

    class Config:
        from_attributes = True
