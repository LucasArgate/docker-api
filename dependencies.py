# dependencies.py
from fastapi import Header
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

seguranca_bearer = HTTPBearer()
TOKEN_VALIDO = "your_valid_token_here" #64 caracter token for example


async def log_de_requisicao(user_agent: str = Header(None)):
    """Dependência simples que imprime o User-Agent de quem fez o pedido."""
    print(f"Novo pedido recebido de: {user_agent}")


async def verificar_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(seguranca_bearer)):
    if credentials.scheme != "Bearer" or credentials.credentials != TOKEN_VALIDO:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials