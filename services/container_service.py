import subprocess
import os
import yaml
import docker
from fastapi import HTTPException
from typing import List, Tuple

from models.container import ContainerOut, ContainerCreate
from services import registry_service

# Caminho onde os projetos docker-compose serão armazenados.
# Mova para um arquivo de configuração central se preferir.
COMPOSE_PROJECT_PATH = os.getenv('COMPOSE_PROJECT_PATH', 'c:/docker-projects')

# Inicializa o cliente Docker
try:
    docker_client = docker.from_env()
except docker.errors.DockerException as e:
    print(f"ERRO: Não foi possível conectar ao Docker daemon: {e}")
    docker_client = None

def _execute_command(command: List[str], working_dir: str, command_input: str = None) -> Tuple[bool, str]:
    """Função auxiliar para executar comandos no shell."""
    print(f"Executando no diretório '{working_dir}': {' '.join(command)}")
    try:
        process = subprocess.run(
            command,
            cwd=working_dir,
            capture_output=True,
            text=True,
            check=True,
            input=command_input,
            encoding='utf-8'
        )
        return True, process.stdout
    except FileNotFoundError:
        msg = f"Erro: O comando '{command[0]}' não foi encontrado. Verifique se o Docker está instalado e no PATH do sistema."
        raise HTTPException(status_code=500, detail=msg)
    except subprocess.CalledProcessError as e:
        return False, f"Erro ao executar o comando.\nSaída: {e.stdout}\nErro: {e.stderr}"

def _execute_with_login(image_name: str, command_to_run: List[str], working_dir: str) -> Tuple[bool, str]:
    """Realiza o login no Docker, executa um comando e depois faz logout."""
    registry_url = image_name.split('/')[0] if '/' in image_name else None
    
    is_private_registry = registry_url and ('.' in registry_url or ':' in registry_url)
    credentials = None

    if is_private_registry:
        credentials = registry_service.get_full_registry_by_url(registry_url)
        if not credentials:
            raise HTTPException(status_code=404, detail=f"Nenhuma credencial encontrada para o registry '{registry_url}'.")

        login_cmd = ["docker", "login", "-u", credentials.login, "--password-stdin", credentials.url]
        login_success, login_out = _execute_command(login_cmd, working_dir, command_input=credentials.password)
        if not login_success:
            return False, f"Falha no login para {registry_url}: {login_out}"
    
    success, output = _execute_command(command_to_run, working_dir)
    
    if is_private_registry and credentials:
        _execute_command(["docker", "logout", credentials.url], working_dir)
            
    return success, output

def _get_image_from_compose(compose_file_path: str, service_name: str) -> str:
    """Lê um arquivo docker-compose.yml e retorna o nome da imagem para um serviço."""
    try:
        with open(compose_file_path, 'r') as f:
            compose_data = yaml.safe_load(f)
        return compose_data['services'][service_name]['image']
    except (FileNotFoundError, yaml.YAMLError, KeyError, TypeError) as e:
        raise HTTPException(status_code=404, detail=f"Erro ao ler imagem do docker-compose para o serviço '{service_name}': {e}")

def list_containers() -> List[ContainerOut]:
    """Lista todos os contêineres Docker."""
    if not docker_client:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao Docker daemon.")
    try:
        containers = docker_client.containers.list(all=True)
        return [
            ContainerOut(
                id=c.short_id, name=c.name,
                image=c.image.tags[0] if c.image.tags else "N/A", status=c.status
            ) for c in containers
        ]
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar contêineres: {e}")

def create_container(container_def: ContainerCreate):
    """Cria um novo serviço/contêiner através de um arquivo docker-compose."""
    service_name = container_def.service_name
    project_path = os.path.join(COMPOSE_PROJECT_PATH, service_name)

    if os.path.exists(project_path):
        raise HTTPException(status_code=409, detail=f"O serviço '{service_name}' já existe.")

    os.makedirs(project_path, exist_ok=True)

    compose_config = {
        'version': '3.8',
        'services': {
            service_name: {
                'image': container_def.image, 'container_name': service_name,
                'restart': container_def.restart_policy
            }
        }
    }
    if container_def.ports:
        compose_config['services'][service_name]['ports'] = container_def.ports
    if container_def.environment:
        compose_config['services'][service_name]['environment'] = container_def.environment
    if container_def.volumes:
        compose_config['services'][service_name]['volumes'] = container_def.volumes
        named_volumes = {v.split(':')[0]: None for v in container_def.volumes if ':' in v and not v.startswith('/')}
        if named_volumes: compose_config['volumes'] = named_volumes
    if container_def.networks:
        compose_config['services'][service_name]['networks'] = container_def.networks
        compose_config['networks'] = {net: {'external': True} for net in container_def.networks}

    try:
        with open(os.path.join(project_path, 'docker-compose.yml'), 'w') as f:
            yaml.dump(compose_config, f, sort_keys=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Não foi possível escrever o arquivo docker-compose.yml: {e}")

    up_cmd = ["docker", "compose", "up", "-d"]
    success, output = _execute_with_login(container_def.image, up_cmd, project_path)
    if not success:
        raise HTTPException(status_code=500, detail=f"Falha ao iniciar o serviço: {output}")

    return {"status": "success", "message": f"Serviço '{service_name}' criado e iniciado!", "project_path": project_path, "compose_config": compose_config}

def recreate_service(service_name: str):
    """Puxa a imagem mais recente e recria um serviço com --force-recreate."""
    project_path = os.path.join(COMPOSE_PROJECT_PATH, service_name)
    if not os.path.isdir(project_path):
        raise HTTPException(status_code=404, detail=f"Diretório do projeto '{project_path}' não encontrado.")
    
    image_name = _get_image_from_compose(os.path.join(project_path, 'docker-compose.yml'), service_name)
    
    pull_cmd = ["docker", "compose", "pull", service_name]
    success_pull, out_pull = _execute_with_login(image_name, pull_cmd, project_path)
    if not success_pull:
        raise HTTPException(status_code=500, detail=f"Falha no pull: {out_pull}")
    
    up_cmd = ["docker", "compose", "up", "-d", "--force-recreate", service_name]
    success_up, out_up = _execute_with_login(image_name, up_cmd, project_path)
    if not success_up:
        raise HTTPException(status_code=500, detail=f"Falha ao recriar o serviço: {out_up}")

    return {"status": "success", "message": f"Serviço '{service_name}' recriado com a imagem '{image_name}'."}

def recreate_standalone_container(container_name: str):
    """Recria um contêiner "standalone", atualizando sua configuração."""
    if not docker_client:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao Docker daemon.")

    try:
        old_container = docker_client.containers.get(container_name)
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail=f"Contêiner '{container_name}' não encontrado.")
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com o Docker: {e}")

    # 1. Inspeciona a configuração
    try:
        inspection_data = docker_client.api.inspect_container(old_container.id)
        config = inspection_data['Config']
        host_config = inspection_data['HostConfig']
        image_name = config['Image']
        container_name = inspection_data['Name'].lstrip('/')
        # Mapeamento de parâmetros para a nova criação
        create_params = {
            'image': image_name,
            'name': container_name,
            'environment': config.get('Env'),
            'ports': host_config.get('PortBindings'),
            'mounts': host_config.get('Mounts'),
            'network_mode': host_config.get('NetworkMode'),
            'restart_policy': host_config.get('RestartPolicy'),
            'detach': True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inspecionar o contêiner: {e}")

    # 2. Puxa a imagem mais recente
    try:
        print(f"Puxando imagem mais recente: {image_name}...")
        docker_client.images.pull(image_name)
    except docker.errors.ImageNotFound:
        print(f"Aviso: Imagem '{image_name}' não encontrada no registry. Usando a imagem local.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao puxar a imagem: {e}")

    # 3. Para e remove o contêiner antigo
    try:
        print(f"Parando e removendo o contêiner antigo: {container_name}...")
        old_container.stop()
        old_container.remove()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parar/remover o contêiner: {e}")

    # 4. Cria o novo contêiner
    try:
        print(f"Recriando o contêiner: {container_name}...")
        new_container = docker_client.containers.run(**create_params)
        return {
            "status": "success",
            "message": f"Contêiner '{new_container.name}' recriado com sucesso com o ID: {new_container.short_id}",
            "new_container_id": new_container.short_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha crítica ao recriar o contêiner: {e}. O contêiner antigo foi removido, mas o novo não pôde ser criado."
        )

def remove_container(container_name: str):
    """Remove a container by its name."""
    if not docker_client:
        raise HTTPException(status_code=500, detail="Could not connect to Docker daemon.")
    try:
        container = docker_client.containers.get(container_name)
        container.remove(force=True)  # Use force=True to remove even if it's running
        return {"status": "success", "message": f"Container '{container_name}' removed successfully."}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail=f"Container '{container_name}' not found.")
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Error removing container: {e}")