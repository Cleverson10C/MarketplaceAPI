from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
motor = create_engine(DATABASE_URL, connect_args=connect_args)

# Cria a classe de sessão para interagir com o banco de dados
SessaoLocal = sessionmaker(bind=motor)

# Base para os modelos do SQLAlchemy
Base = declarative_base()
