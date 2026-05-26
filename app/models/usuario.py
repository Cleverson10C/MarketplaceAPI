from sqlalchemy import Column, String, Integer, Boolean
from app.banco.session import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    role = Column(String, nullable=False, default="usuario")
