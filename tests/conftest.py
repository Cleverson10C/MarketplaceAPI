import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import aut_rotas
from app.api.routes import rotas_produto
from app.banco.session import Base
from app.core.config import DATABASE_URL
from app.core import dependencies
from app.main import app
from app.models import item_pedido, movimento_estoque, pedido, produto, rastreamento_produto, usuario  # noqa: F401

USE_MAIN_DB = os.getenv("TEST_USE_MAIN_DB", "false").lower() == "true"
TEST_DB_URL = DATABASE_URL if USE_MAIN_DB else os.getenv("TEST_DATABASE_URL", "sqlite:///./test_suite.db")
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[dependencies.get_db] = override_get_db
    app.dependency_overrides[aut_rotas.get_db] = override_get_db
    app.dependency_overrides[rotas_produto.obter_banco] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
