# Docker API - Automação e Gerenciamento Simplificado

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Uma API leve, escrita em FastAPI, para gerenciar e automatizar seus contêineres Docker. Este projeto nasceu da necessidade de uma ferramenta simples e programável para orquestrar deployments, servindo como uma alternativa agnóstica a UIs complexas como o Portainer, com foco total em automação e integração com pipelines de CI/CD.

A principal motivação é capacitar desenvolvedores a automatizarem seus fluxos de trabalho. Imagine atualizar sua aplicação em produção com um simples `git push`, onde o GitHub Actions constrói sua nova imagem Docker, a envia para um registry privado e, em seguida, notifica esta API para recriar o contêiner com a nova versão. **É exatamente para isso que esta API foi projetada.**

## ✨ Funcionalidades Principais

*   **Gerenciamento de Registries**: Armazene com segurança as credenciais de seus registries privados.
*   **Deploy via Docker Compose**: Crie serviços complexos a partir de uma simples definição JSON. A API gera o `docker-compose.yml` e orquestra o deploy.
*   **Atualização Contínua (CI/CD)**: Endpoints dedicados para recriar serviços (`/recreate`) e contêineres standalone (`/update`), puxando a imagem mais recente do registry.
*   **Operações CRUD**: Liste, crie, edite e remova contêineres e registries através de uma API RESTful.
*   **Segurança**: Proteção de endpoints com autenticação via Bearer Token.

## 🚀 Começando

Siga os passos abaixo para ter a API rodando em seu ambiente.

### Pré-requisitos

*   Docker
*   Docker Compose v2+
*   Python 3.9+

### 1. Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/LucasArgate/docker-api.git
cd docker-api

# 2. Crie um ambiente virtual e instale as dependências
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Crie um diretório para os projetos Docker
# Este é o diretório que a API usará para criar os arquivos docker-compose.yml
mkdir c:/docker-projects 

# 4. Configure o token de segurança
# Crie um arquivo .env na raiz e adicione seu token
# Exemplo de .env:
# API_BEARER_TOKEN=seu-token-super-secreto

# 5. Inicie a API
python -m uvicorn main:app --reload --host 0.0.0.0 --port 5001

# A API estará disponível em http://localhost:5001
```

### 2. Rodando com Docker Compose (Recomendado)

A maneira mais fácil de rodar em produção é usando o `docker-compose.yml` fornecido.

```bash
# 1. Certifique-se de que o diretório de projetos exista no seu host
# Ex: /home/ubuntu/docker-projects

# 2. Configure a variável COMPOSE_PROJECT_PATH no docker-compose.yml
# para apontar para o diretório criado acima.

# 3. Inicie o serviço
docker compose up -d
```

# 3. Compilando sua imagem :)
```
 sudo docker compose up -d --build --force-recreate
```

## 🤖 Caso de Uso: Automação de Deploy com GitHub Actions

Este é o coração do projeto. Veja como automatizar o deploy de uma aplicação (`my-awesome-app`) sempre que uma nova versão for enviada para a branch `main`.

1.  **Cadastre seu Registry na API**: Primeiro, adicione as credenciais do seu Docker Hub, GitHub Container Registry, etc., à nossa API usando o endpoint `POST /registry`.

2.  **Configure os Secrets no GitHub**: No seu repositório, vá em `Settings > Secrets and variables > Actions` e adicione os seguintes secrets:
    *   `DOCKER_API_URL`: A URL da sua API (ex: `http://seu-servidor.com:5001`).
    *   `DOCKER_API_TOKEN`: O token Bearer que você configurou no arquivo `.env`.

3.  **Crie o Workflow**: Adicione o seguinte arquivo em `.github/workflows/deploy.yml` no repositório da sua aplicação.

    ```yaml
    name: Build and Deploy

    on:
      push:
        branches: [ main ]

    jobs:
      build-and-push:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout code
            uses: actions/checkout@v3

          - name: Login to Docker Hub
            uses: docker/login-action@v2
            with:
              username: ${{ secrets.DOCKER_USERNAME }}
              password: ${{ secrets.DOCKER_PASSWORD }}

          - name: Build and push Docker image
            uses: docker/build-push-action@v4
            with:
              context: .
              push: true
              tags: seu-usuario/my-awesome-app:latest

      deploy:
        needs: build-and-push
        runs-on: ubuntu-latest
        steps:
          - name: Trigger API to recreate the container
            run: |
              curl -X POST \
                "${{ secrets.DOCKER_API_URL }}/containers/recreate/my-awesome-app" \
                -H "Authorization: Bearer ${{ secrets.DOCKER_API_TOKEN }}" \
                -H "Content-Type: application/json"
    ```

Agora, toda vez que você fizer um push para a `main`, o GitHub Actions irá:
1.  Construir a nova imagem da sua aplicação.
2.  Enviá-la para o Docker Hub.
3.  Fazer uma chamada segura para a nossa API.
4.  A API irá puxar a nova imagem e recriar o contêiner, completando o ciclo de deploy automatizado!

## 📚 Documentação da API

A API é auto-documentada usando Swagger UI. Após iniciar a aplicação, acesse `http://localhost:5001/docs` para ver todos os endpoints, modelos e testá-los interativamente.

### Endpoints Principais

| Método | Endpoint                               | Descrição                                                    |
| :----- | :------------------------------------- | :----------------------------------------------------------- |
| `GET`    | `/containers`                          | Lista todos os contêineres no host.                            |
| `POST`   | `/containers/create`                   | Cria um novo serviço a partir de uma definição JSON.             |
| `POST`   | `/containers/recreate/{service_name}`  | Puxa a imagem mais recente e recria um serviço Compose.        |
| `PUT`    | `/containers/{container_name}`         | Edita um contêiner standalone com novas configurações.        |
| `DELETE` | `/containers/{container_name}`         | Remove um contêiner.                                         |
| `GET`    | `/registry`                            | Lista todos os registries configurados.                      |
| `POST`   | `/registry`                            | Adiciona as credenciais de um novo registry.                  |
| `DELETE` | `/registry/{registry_name}`            | Remove um registry.                                          |

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Sinta-se à vontade para abrir uma *issue* para relatar bugs ou sugerir novas funcionalidades. Se você quiser contribuir com código, por favor, abra um *Pull Request*.

## 📜 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🗺️ Roadmap Futuro

Aqui estão algumas das funcionalidades e melhorias planejadas para o futuro do projeto:

-   **Gerenciamento de Registry Local**:
    -   Criar um registry privado local usando a imagem `registry:2` com autenticação.
    -   **Atualização Automática de Imagens**:
        -   Detectar quando uma nova imagem é enviada para um registry.
        -   Para contêineres configurados para sempre puxar a imagem (`always pull`), atualizá-los automaticamente quando uma nova versão estiver disponível.
-   **Onboarding e Gerenciamento de Usuários**:
    -   Criar um endpoint de instalação (`/install`) para a configuração inicial.
    -   Permitir a criação de um usuário `root` com senha na primeira execução.
    -   Implementar um CRUD completo para gerenciamento de usuários.
-   **Suporte a Múltiplos Nós (Multi-node)**:
    -   Adicionar a capacidade de gerenciar recursos (CPU, GPU, Memória) em diferentes nós a partir de uma única API.
-   **Sistema de Webhooks**:
    -   Implementar um sistema de CRUD para webhooks, permitindo que a API notifique sistemas externos sobre eventos (ex: contêiner criado, atualizado, etc.).
-   **Interface com IA Generativa**:
    -   Desenvolver uma view ou CLI interativa que utilize IA generativa para simplificar a criação de contêineres e configurações, reduzindo a necessidade de criar JSONs manualmente.