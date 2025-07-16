from fastapi import APIRouter, Depends, HTTPException
from typing import List

from dependencies import log_de_requisicao
from models.registry import Registry, RegistryOut
from services import registry_service

# Criamos um "router", que é como um mini-aplicativo FastAPI.
router = APIRouter(
    prefix="/registry",
    tags=["Registry"],
    dependencies=[Depends(log_de_requisicao)],
)

@router.get("/", response_model=List[RegistryOut])
def list_registries():
    """Endpoint para listar todos os registries."""
    return registry_service.list_registries()

@router.get("/{registry_name}", response_model=RegistryOut)
def get_registry(registry_name: str):
    """Endpoint para obter um registry pelo nome."""
    registry = registry_service.get_registry_by_name(registry_name)
    if not registry:
        raise HTTPException(
            status_code=404, detail=f"Registry com o nome '{registry_name}' não encontrado."
        )
    return registry

@router.post("/", response_model=RegistryOut, status_code=201)
def create_registry(registry: Registry):
    """Endpoint para criar um novo registry."""
    
    return registry_service.create_registry(registry)

@router.delete("/{registry_name}", status_code=204)
def delete_registry(registry_name: str):
    """Endpoint para remover um registry existente pelo nome."""
    registry_service.delete_registry(registry_name)