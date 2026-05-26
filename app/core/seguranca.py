from passlib.context import CryptContext

# usa PBKDF2-SHA256 para evitar problemas com o backend bcrypt local
contexto_criptografia = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def gerar_hash_senha(senha: str) -> str:
    return contexto_criptografia.hash(senha)

def verificar_senha(senha: str, hash_senha: str) -> bool:
    return contexto_criptografia.verify(senha, hash_senha)