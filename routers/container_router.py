from fastapi import APIRouter, Depends, Body
from typing import List


from dependencies import verificar_bearer_token
from models.container import ContainerOut, ContainerCreate, ActionResponse, CreateActionResponse
from services import container_service

router = APIRouter(
    prefix="/containers",
    tags=["Containers"],
    dependencies=[Depends(verificar_bearer_token)],
)

@router.get("/", response_model=List[ContainerOut])
def list_all_containers():
    """Lista todos os contêineres Docker, em execução ou parados."""
    return container_service.list_containers()

@router.post("/create", response_model=CreateActionResponse, status_code=201)
def create_new_container(
    container_definition: ContainerCreate = Body(...)
):
    """Cria um novo serviço a partir de uma definição em JSON, usando docker-compose."""
    return container_service.create_container(container_definition)

@router.post("/recreate/{service_name}", response_model=ActionResponse)
def recreate_container_service(service_name: str):
    """Puxa a imagem mais recente e recria um serviço com 'force-recreate'."""
    return container_service.recreate_standalone_container(service_name)

@router.put("/{container_name}", response_model=ActionResponse)
def update_standalone_container(container_name: str):
    """Recria um contêiner standalone, atualizando sua configuração."""
    # Note que usamos PUT para representar a atualização do recurso.
    return container_service.recreate_service(container_name)

@router.delete("/{container_name}", response_model=ActionResponse)
def delete_container(container_name: str):
    """Remove a container by its name."""
    return container_service.remove_container(container_name)