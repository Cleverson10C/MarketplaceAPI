from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.banco.session import Base


class MovimentoEstoque(Base):
    __tablename__ = "movimentos_estoque"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    tipo = Column(String, nullable=False)  # entrada | saida | ajuste
    quantidade = Column(Integer, nullable=False)
    estoque_antes = Column(Integer, nullable=False)
    estoque_depois = Column(Integer, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
