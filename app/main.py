import logging
import time

from fastapi import FastAPI
from fastapi import Request

from app.api.routes.rotas_produto import roteador
from app.api.routes import rotas_pedido
from app.banco.session import Base, motor
from app.api.routes import aut_rotas
from app.core.logging_config import setup_logging
from app.models import item_pedido, movimento_estoque, pedido, produto, rastreamento_produto, usuario

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Marketplace API",
    description="API de marketplace com pedidos e rastreamento",
    version="1.0.0",
)

app.include_router(rotas_pedido.router)
app.include_router(aut_rotas.router)
app.include_router(roteador)

# Cria tabelas automaticamente (somente desenvolvimento)
Base.metadata.create_all(bind=motor)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    inicio = time.perf_counter()
    resposta = await call_next(request)
    duracao_ms = (time.perf_counter() - inicio) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        resposta.status_code,
        duracao_ms,
    )
    return resposta

@app.get("/")
def ler_raiz():
    return {"mensagem": "Marketplace API rodando!"}
