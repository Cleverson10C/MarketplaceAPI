from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.banco.session import SessaoLocal
from app.schemas.produto import (
    MovimentoEstoqueCriacao,
    MovimentoEstoqueResposta,
    ProdutoAtualizacao,
    ProdutoCriacao,
    ProdutoResposta,
    RastreamentoProdutoCriacao,
    RastreamentoProdutoResposta,
)
from app.repositories.repositorio_produto import (
    atualizar_produto,
    criar_produto,
    deletar_produto,
    listar_rastreamentos_produto,
    listar_produtos_abaixo_estoque_minimo,
    listar_movimentos_estoque,
    listar_produtos,
    movimentar_estoque,
    registrar_rastreamento_produto,
)
from app.core.dependencies import get_usuario_logado

roteador = APIRouter(prefix="/products", tags=["Produtos"])


def obter_banco():
    banco = SessaoLocal()
    try:
        yield banco
    finally:
        banco.close()


@roteador.post("/", response_model=ProdutoResposta, summary="Criar produto")
def criar(produto: ProdutoCriacao, banco: Session = Depends(obter_banco), usuario=Depends(get_usuario_logado)):
    return criar_produto(banco, produto.nome, produto.preco, produto.quantidade, produto.estoque_minimo)


@roteador.get("/", response_model=list[ProdutoResposta], summary="Listar produtos")
def listar_todos(banco: Session = Depends(obter_banco)):
    return listar_produtos(banco)


@roteador.get("/{produto_id}", response_model=ProdutoResposta, summary="Obter produto por ID")
def obter_por_id(produto_id: int, banco: Session = Depends(obter_banco)):
    from app.repositories.repositorio_produto import obter_produto_por_id
    produto = obter_produto_por_id(banco, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@roteador.put("/{produto_id}", response_model=ProdutoResposta, summary="Atualizar produto")
def atualizar(produto_id: int, produto_dados: ProdutoAtualizacao, banco: Session = Depends(obter_banco), usuario=Depends(get_usuario_logado)):
    produto = atualizar_produto(
        banco,
        produto_id,
        produto_dados.nome,
        produto_dados.preco,
        produto_dados.estoque_minimo,
    )
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@roteador.delete("/{produto_id}", status_code=204, summary="Deletar produto")
def deletar(produto_id: int, banco: Session = Depends(obter_banco), usuario=Depends(get_usuario_logado)):
    sucesso = deletar_produto(banco, produto_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return None


@roteador.post(
    "/{produto_id}/estoque",
    response_model=MovimentoEstoqueResposta,
    summary="Movimentar estoque (entrada/saída/ajuste)",
)
def movimentar(
    produto_id: int,
    movimento: MovimentoEstoqueCriacao,
    banco: Session = Depends(obter_banco),
    usuario=Depends(get_usuario_logado),
):
    try:
        resultado = movimentar_estoque(banco, produto_id, movimento.tipo, movimento.quantidade)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))

    if not resultado:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return resultado


@roteador.get(
    "/{produto_id}/estoque/movimentos",
    response_model=list[MovimentoEstoqueResposta],
    summary="Listar movimentos de estoque",
)
def listar_movimentos(
    produto_id: int,
    banco: Session = Depends(obter_banco),
    usuario=Depends(get_usuario_logado),
):
    from app.repositories.repositorio_produto import obter_produto_por_id

    produto = obter_produto_por_id(banco, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return listar_movimentos_estoque(banco, produto_id)


@roteador.get(
    "/estoque/alertas",
    response_model=list[ProdutoResposta],
    summary="Listar produtos abaixo do estoque mínimo",
)
def listar_alertas_estoque(
    banco: Session = Depends(obter_banco),
    usuario=Depends(get_usuario_logado),
):
    return listar_produtos_abaixo_estoque_minimo(banco)


@roteador.post(
    "/{produto_id}/rastreamentos",
    response_model=RastreamentoProdutoResposta,
    summary="Registrar rastreamento de produto",
)
def registrar_rastreamento(
    produto_id: int,
    dados: RastreamentoProdutoCriacao,
    banco: Session = Depends(obter_banco),
    usuario=Depends(get_usuario_logado),
):
    rastreamento = registrar_rastreamento_produto(
        banco,
        produto_id,
        dados.status,
        dados.localizacao,
        dados.observacao,
    )
    if not rastreamento:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return rastreamento


@roteador.get(
    "/{produto_id}/rastreamentos",
    response_model=list[RastreamentoProdutoResposta],
    summary="Listar rastreamentos do produto",
)
def listar_rastreamentos(
    produto_id: int,
    banco: Session = Depends(obter_banco),
    usuario=Depends(get_usuario_logado),
):
    from app.repositories.repositorio_produto import obter_produto_por_id

    produto = obter_produto_por_id(banco, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return listar_rastreamentos_produto(banco, produto_id)
