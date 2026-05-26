from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.banco.session import SessaoLocal
from app.models.usuario import Usuario
from app.core.config import ALGORITHM, SECRET_KEY

security = HTTPBearer()

def get_db():
    db = SessaoLocal()
    try:
        yield db
    finally:
        db.close()

def get_usuario_logado(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = creds.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Usuário inativo")

    return usuario

def get_admin_logado(usuario: Usuario = Depends(get_usuario_logado)):
    if usuario.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return usuario
