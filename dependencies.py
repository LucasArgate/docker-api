# dependencies.py
import os
from fastapi import Header
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

seguranca_bearer = HTTPBearer()
PUBLIC_API_KEY = os.getenv("PUBLIC_API_KEY") #by my friend THI

async def log_de_requisicao(user_agent: str = Header(None)):
    """Dependência simples que imprime o User-Agent de quem fez o pedido."""
    # Este log foi comentado para não gerar informações em excesso.
    # print(f"Novo pedido recebido de: {user_agent}")
    pass


async def verificar_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(seguranca_bearer)):
    if credentials.scheme != "Bearer" or credentials.credentials != PUBLIC_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials