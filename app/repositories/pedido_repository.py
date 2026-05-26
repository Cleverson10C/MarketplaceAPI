from sqlalchemy.orm import Session

from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido
from app.models.produto import Produto
from app.repositories.repositorio_produto import registrar_movimento_estoque, registrar_rastreamento_produto

def criar_pedido(db: Session, usuario_id: int, itens: list):
    pedido = Pedido(usuario_id=usuario_id)
    db.add(pedido)
    db.flush()

    total = 0

    for item in itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()

        if not produto:
            raise ValueError(f"Produto {item.produto_id} não encontrado")
        if produto.estoque < item.quantidade:
            raise ValueError(f"Estoque insuficiente para o produto {produto.id}")

        subtotal = produto.preco * item.quantidade
        total += subtotal

        item_pedido = ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=item.quantidade,
            preco=produto.preco
        )

        db.add(item_pedido)
        registrar_movimento_estoque(db, produto, "saida", item.quantidade, auto_commit=False)
        registrar_rastreamento_produto(
            db,
            produto.id,
            "pedido_criado",
            f"Pedido #{pedido.id}",
            f"Baixa automática de {item.quantidade} unidade(s) no pedido",
            auto_commit=False,
        )

    pedido.total = total
    db.commit()
    db.refresh(pedido)

    return pedido
