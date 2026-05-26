from sqlalchemy.orm import Session
from app.models.usuario import Usuario

def criar_usuario(db: Session, email: str, senha: str):
    usuario = Usuario(email=email, senha=senha, ativo=True, role="usuario")
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def buscar_usuario_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()


def buscar_usuario_por_id(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def desativar_usuario(db: Session, usuario: Usuario):
    usuario.ativo = False
    db.commit()
    db.refresh(usuario)
    return usuario


def deletar_usuario(db: Session, usuario: Usuario):
    db.delete(usuario)
    db.commit()


def listar_usuarios(db: Session):
    return db.query(Usuario).filter(Usuario.ativo == True).all()
