# main.py

# 1. Importações necessárias
import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Dict

from routers import registry_router, container_router
from dependencies import verificar_bearer_token

app = FastAPI(
    title="Docker API",
    description="Api for docker management and MCP integrations",
    dependencies=[Depends(verificar_bearer_token)],
)

# Adicionando os routers à aplicação
app.include_router(registry_router.router)
app.include_router(container_router.router)

# Endpoint Raiz (GET /)
@app.get("/")
def ler_raiz():
    """
    Este é o endpoint principal. Retorna uma mensagem de boas-vindas.
    """
    return {"mensagem": "Bem-vindo à minha primeira API com FastAPI! X"}

# Bloco para iniciar o servidor programaticamente (opcional)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
