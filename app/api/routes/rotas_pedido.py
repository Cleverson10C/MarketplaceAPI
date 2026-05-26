from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_usuario_logado
from app.schemas.pedido import PedidoCriar, PedidoResposta
from app.repositories.pedido_repository import criar_pedido

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("/", response_model=PedidoResposta)
async def criar(
    pedido: PedidoCriar,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado),
):
    '''
    Somente usuários autenticados podem criar pedidos. O pedido deve 
    conter uma lista de itens, cada um com o ID do produto e a quantidade
    desejada.
    '''
    try:
        novo_pedido = criar_pedido(db, usuario.id, pedido.itens)
    except ValueError as erro:
        mensagem = str(erro)
        if "não encontrado" in mensagem:
            raise HTTPException(status_code=404, detail=mensagem)
        if "Estoque insuficiente" in mensagem:
            raise HTTPException(status_code=409, detail=mensagem)
        raise HTTPException(status_code=400, detail=mensagem)
    return novo_pedido
