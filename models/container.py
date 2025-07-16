from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ContainerOut(BaseModel):
    id: str
    name: str
    image: str
    status: str

class ContainerCreate(BaseModel):
    service_name: str = Field(..., description="Nome do serviço e do contêiner.")
    image: str = Field(..., description="Imagem Docker a ser usada (ex: 'meuregistry.com/app:latest').")
    restart_policy: str = Field("unless-stopped", description="Política de reinicialização (ex: 'always', 'unless-stopped').")
    ports: Optional[List[str]] = Field(None, description="Lista de portas a serem mapeadas (ex: ['8080:80']).")
    environment: Optional[List[str]] = Field(None, description="Lista de variáveis de ambiente (ex: ['DB_HOST=localhost']).")
    volumes: Optional[List[str]] = Field(None, description="Lista de volumes a serem montados (ex: ['data_volume:/var/data', './config:/app/config']).")
    networks: Optional[List[str]] = Field(None, description="Lista de redes para se conectar.")

class ActionResponse(BaseModel):
    status: str
    message: str

class CreateActionResponse(ActionResponse):
    project_path: Optional[str] = None
    compose_config: Optional[Dict] = None