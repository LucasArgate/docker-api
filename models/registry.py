from pydantic import BaseModel

# Modelo para receber os dados, incluindo a senha
class Registry(BaseModel):
    name: str
    url: str
    login: str
    password: str

# Modelo para expor os dados na API, omitindo a senha por segurança
class RegistryOut(BaseModel):
    name: str
    url: str
    login: str