from sqlalchemy.orm import Session

from app.models.movimento_estoque import MovimentoEstoque
from app.models.produto import Produto
from app.models.rastreamento_produto import RastreamentoProduto


def criar_produto(sessao: Session, nome: str, preco: float, quantidade: int, estoque_minimo: int):
    produto = Produto(nome=nome, preco=preco, estoque=quantidade, estoque_minimo=estoque_minimo)
    sessao.add(produto)
    sessao.commit()
    sessao.refresh(produto)

    if quantidade > 0:
        movimento = MovimentoEstoque(
            produto_id=produto.id,
            tipo="entrada",
            quantidade=quantidade,
            estoque_antes=0,
            estoque_depois=quantidade,
        )
        sessao.add(movimento)
        sessao.commit()

    return produto


def listar_produtos(sessao: Session):
    return sessao.query(Produto).all()


def obter_produto_por_id(sessao: Session, produto_id: int):
    return sessao.query(Produto).filter(Produto.id == produto_id).first()


def atualizar_produto(
    sessao: Session, produto_id: int, nome: str = None, preco: float = None, estoque_minimo: int = None
):
    produto = obter_produto_por_id(sessao, produto_id)
    if not produto:
        return None
    if nome is not None:
        produto.nome = nome
    if preco is not None:
        produto.preco = preco
    if estoque_minimo is not None:
        produto.estoque_minimo = estoque_minimo
    sessao.commit()
    sessao.refresh(produto)
    return produto


def deletar_produto(sessao: Session, produto_id: int):
    produto = obter_produto_por_id(sessao, produto_id)
    if not produto:
        return False
    sessao.delete(produto)
    sessao.commit()
    return True


def registrar_movimento_estoque(
    sessao: Session, produto: Produto, tipo: str, quantidade: int, auto_commit: bool = True
):
    estoque_antes = produto.estoque

    if tipo == "entrada":
        estoque_depois = estoque_antes + quantidade
    elif tipo == "saida":
        if quantidade > estoque_antes:
            raise ValueError("Estoque insuficiente para saída")
        estoque_depois = estoque_antes - quantidade
    elif tipo == "ajuste":
        estoque_depois = quantidade
    else:
        raise ValueError("Tipo de movimento inválido")

    produto.estoque = estoque_depois
    movimento = MovimentoEstoque(
        produto_id=produto.id,
        tipo=tipo,
        quantidade=quantidade,
        estoque_antes=estoque_antes,
        estoque_depois=estoque_depois,
    )
    sessao.add(movimento)
    if auto_commit:
        sessao.commit()
        sessao.refresh(movimento)
        sessao.refresh(produto)
    return movimento


def movimentar_estoque(sessao: Session, produto_id: int, tipo: str, quantidade: int):
    produto = obter_produto_por_id(sessao, produto_id)
    if not produto:
        return None
    return registrar_movimento_estoque(sessao, produto, tipo, quantidade, auto_commit=True)


def listar_movimentos_estoque(sessao: Session, produto_id: int):
    return (
        sessao.query(MovimentoEstoque)
        .filter(MovimentoEstoque.produto_id == produto_id)
        .order_by(MovimentoEstoque.id.desc())
        .all()
    )


def listar_produtos_abaixo_estoque_minimo(sessao: Session):
    return sessao.query(Produto).filter(Produto.estoque <= Produto.estoque_minimo).all()


def registrar_rastreamento_produto(
    sessao: Session,
    produto_id: int,
    status: str,
    localizacao: str,
    observacao: str | None = None,
    auto_commit: bool = True,
):
    produto = obter_produto_por_id(sessao, produto_id)
    if not produto:
        return None

    rastreamento = RastreamentoProduto(
        produto_id=produto_id,
        status=status,
        localizacao=localizacao,
        observacao=observacao,
    )
    sessao.add(rastreamento)
    if auto_commit:
        sessao.commit()
        sessao.refresh(rastreamento)
    return rastreamento


def listar_rastreamentos_produto(sessao: Session, produto_id: int):
    return (
        sessao.query(RastreamentoProduto)
        .filter(RastreamentoProduto.produto_id == produto_id)
        .order_by(RastreamentoProduto.id.desc())
        .all()
    )
