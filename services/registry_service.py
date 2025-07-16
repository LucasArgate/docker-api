import json
from typing import List, Optional
from fastapi import HTTPException

from models.registry import Registry, RegistryOut  # Assumindo que os modelos estão em models/registry.py

REGISTRIES_FILE = "data/registries.json"

def carregar_registries() -> List[dict]:
    try:
        with open(REGISTRIES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def salvar_registries(registries: List[dict]):
    with open(REGISTRIES_FILE, "w") as f:
        json.dump(registries, f, indent=4)

def list_registries() -> List[RegistryOut]:
    registries = carregar_registries()
    return [RegistryOut(**r) for r in registries]

def create_registry(registry: Registry) -> RegistryOut:
    registries = carregar_registries()
    if any(r["name"] == registry.name for r in registries):
        raise HTTPException(
            status_code=409, detail=f"Registry com o nome '{registry.name}' já existe."
        )
    registries.append(registry.dict())
    salvar_registries(registries)
    return RegistryOut(**registry.dict())

def delete_registry(registry_name: str):
    registries = carregar_registries()
    initial_length = len(registries)
    registries = [r for r in registries if r["name"] != registry_name]
    if len(registries) < initial_length:
        salvar_registries(registries)
    else:
        raise HTTPException(status_code=404, detail="Registry não encontrado")

def get_registry_by_name(registry_name: str) -> Optional[RegistryOut]:
    registries = carregar_registries()
    for registry in registries:
        if registry["name"] == registry_name:
            return RegistryOut(**registry)
    return None


def get_registry_by_name_with_password(registry_name: str) -> Optional[Registry]:
    registries = carregar_registries()
    for registry in registries:
        if registry["name"] == registry_name:
            return Registry(**registry)
    return None

def get_full_registry_by_url(url_prefix: str) -> Optional[Registry]:
    """Encontra as credenciais completas de um registry pelo seu URL."""
    registries = carregar_registries()
    for registry_data in registries:
        if registry_data.get("url") == url_prefix:
            return Registry(**registry_data)
    return None