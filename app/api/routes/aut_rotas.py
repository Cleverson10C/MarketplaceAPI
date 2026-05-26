import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.schemas.usuario import UsuarioCriar, UsuarioLogin, UsuarioResposta
from app.repositories.usuario_repository import (
    buscar_usuario_por_id,
    buscar_usuario_por_email,
    criar_usuario,
    deletar_usuario,
    desativar_usuario,
    listar_usuarios,
)
import app.core.seguranca
from app.core.token import criar_token
from app.banco.session import SessaoLocal
from app.core.dependencies import get_admin_logado, get_usuario_logado

router = APIRouter(prefix="/auth", tags=["Autenticação"])
logger = logging.getLogger(__name__)

def get_db():
    banco = SessaoLocal()
    try:
        yield banco
    finally:
        banco.close()

@router.post("/registro")
def registrar(usuario: UsuarioCriar, db: Session = Depends(get_db)):
    usuario_existente = buscar_usuario_por_email(db, usuario.email)
    
    if usuario_existente:
        logger.warning("Tentativa de registro com email já cadastrado: %s", usuario.email)
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    senha_hash = app.core.seguranca.gerar_hash_senha(usuario.senha)
    novo_usuario = criar_usuario(db, usuario.email, senha_hash)
    logger.info("Novo usuário registrado com id=%s email=%s", novo_usuario.id, novo_usuario.email)

    return {"mensagem": "Usuário criado com sucesso"}

@router.post("/login")
def login(dados: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = buscar_usuario_por_email(db, dados.email)

    if not usuario or not app.core.seguranca.verificar_senha(dados.senha, usuario.senha):
        logger.warning("Falha de login para email=%s", dados.email)
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not usuario.ativo:
        logger.warning("Tentativa de login com usuário inativo email=%s", dados.email)
        raise HTTPException(status_code=403, detail="Usuário inativo")

    token = criar_token({"sub": usuario.email})
    logger.info("Login realizado com sucesso para usuario_id=%s", usuario.id)

    return {"access_token": token, "token_type": "bearer"}


@router.delete("/me")
def deletar_minha_conta(
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    desativar_usuario(db, usuario)
    return {"mensagem": "Conta desativada com sucesso"}


@router.get("/me", response_model=UsuarioResposta)
def buscar_me(usuario=Depends(get_usuario_logado)):
    return usuario


@router.get("/usuarios", response_model=list[UsuarioResposta])
def buscar_usuarios(
    _admin=Depends(get_admin_logado),
    db: Session = Depends(get_db),
):
    return listar_usuarios(db)


@router.delete("/usuarios/{usuario_id}")
def deletar_usuario_por_id(
    usuario_id: int,
    _admin=Depends(get_admin_logado),
    db: Session = Depends(get_db),
):
    usuario = buscar_usuario_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    try:
        deletar_usuario(db, usuario)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não foi possível deletar usuário com dados relacionados",
        )

    return {"mensagem": "Usuário deletado com sucesso"}
