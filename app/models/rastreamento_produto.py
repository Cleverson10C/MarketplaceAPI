from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.banco.session import Base


class RastreamentoProduto(Base):
    __tablename__ = "rastreamentos_produto"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    status = Column(String, nullable=False)
    localizacao = Column(String, nullable=False)
    observacao = Column(String, nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
