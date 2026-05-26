from pydantic import BaseModel, EmailStr

class UsuarioCriar(BaseModel):
    email: EmailStr
    senha: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class UsuarioResposta(BaseModel):
    id: int
    email: EmailStr
    ativo: bool
    role: str

    class Config:
        from_attributes = True
