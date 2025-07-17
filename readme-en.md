# Docker API - Simplified Automation and Management

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Veja nossa [Versão em português](readme.md) !

A lightweight API, written in FastAPI, to manage and automate your Docker containers. This project was born from the need for a simple, programmable tool to orchestrate deployments, serving as an agnostic alternative to complex UIs like Portainer, with a primary focus on automation and integration with CI/CD pipelines.

The core motivation is to empower developers to automate their workflows. Imagine updating your production application with a simple `git push`, where GitHub Actions builds your new Docker image, pushes it to a private registry, and then notifies this API to recreate the container with the new version. **This API is designed precisely for that purpose.**

## ✨ Key Features

*   **Registry Management**: Securely store credentials for your private registries.
*   **Deploy via Docker Compose**: Create complex services from a simple JSON definition. The API generates the `docker-compose.yml` and orchestrates the deployment.
*   **Continuous Update (CI/CD)**: Dedicated endpoints to recreate services (`/recreate`) and standalone containers (`/update`), pulling the latest image from the registry.
*   **CRUD Operations**: List, create, edit, and remove containers and registries through a RESTful API.
*   **Security**: Endpoint protection with Bearer Token authentication.

## 🚀 Getting Started

```yaml

version: '3.8'

services:
  docker-api:

    image: lucasargate/docker-api:latest
    container_name: docker-api-service
    restart: unless-stopped
    ports:
      - "5001:5001"
    volumes:
      # Mapeia o socket do Docker do host para o contêiner.
      # NECESSÁRIO para que a API possa gerenciar os contêineres do host.
      - /var/run/docker.sock:/var/run/docker.sock

      # Mapeia um diretório no host para dentro do contêiner.
      # A API irá criar os arquivos docker-compose.yml dos seus serviços aqui.
      # CRIE ESTE DIRETÓRIO: ./docker-projects no mesmo local do docker-compose.yml
      - ./docker-projects:/app/projects
    environment:
      # Defina a chave de API pública que será usada para autenticar os pedidos.
      - PUBLIC_API_KEY=YOUR_API_KEY_HERE
      # Define o caminho DENTRO do contêiner onde os projetos serão salvos.
      - COMPOSE_PROJECT_PATH=/app/projects    
```



Follow the steps below to get the API running in your environment.

### Prerequisites

*   Docker
*   Docker Compose v2+
*   Python 3.9+

### 1. Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/LucasArgate/docker-api.git
cd docker-api

# 2. Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Create a directory for Docker projects
# This is where the API will generate docker-compose.yml files
mkdir c:/docker-projects 

# 4. Configure the security token
# Create a .env file in the root and add your token
# Example .env:
# API_BEARER_TOKEN=your-super-secret-token

# 5. Start the API
python -m uvicorn main:app --reload --host 0.0.0.0 --port 5001

# The API will be available at http://localhost:5001
```

### 2. Running with Docker Compose (Recommended)

The easiest way to run in production is using the provided `docker-compose.yml`.

```bash
# 1. Ensure that the project directory exists on your host
# E.g., /home/ubuntu/docker-projects

# 2. Configure the COMPOSE_PROJECT_PATH variable in docker-compose.yml
# to point to the directory created above.

# 3. Start the service
docker compose up -d
```

## 🤖 Use Case: Automated Deployment with GitHub Actions

This is the project's centerpiece. See how to automate the deployment of an application (`my-awesome-app`) whenever a new version is pushed to the `main` branch.

1.  **Register your Registry in the API**: First, add the credentials for your Docker Hub, GitHub Container Registry, etc., to our API using the `POST /registry` endpoint.

2.  **Configure Secrets in GitHub**: In your repository, go to `Settings > Secrets and variables > Actions` and add the following secrets:
    *   `DOCKER_API_URL`: The URL of your API (e.g., `http://your-server.com:5001`).
    *   `DOCKER_API_TOKEN`: The Bearer Token you configured in the `.env` file.

3.  **Create the Workflow**: Add the following file to `.github/workflows/deploy.yml` in your application's repository.

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
              tags: your-user/my-awesome-app:latest

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

Now, every time you push to `main`, GitHub Actions will:
1.  Build the new image of your application.
2.  Push it to Docker Hub.
3.  Make a secure call to our API.
4.  The API will pull the new image and recreate the container, completing the automated deployment cycle!

## 📚 API Documentation

The API is self-documented using Swagger UI. After starting the application, access `http://localhost:5001/docs` to see all endpoints, models, and test them interactively.

### Main Endpoints

| Method | Endpoint                               | Description                                                    |
| :----- | :------------------------------------- | :----------------------------------------------------------- |
| `GET`    | `/containers`                          | Lists all containers on the host.                            |
| `POST`   | `/containers/create`                   | Creates a new service from a JSON definition.                |
| `POST`   | `/containers/recreate/{service_name}`  | Pulls the latest image and recreates a Compose service.       |
| `PUT`    | `/containers/{container_name}`         | Edits a standalone container with new configurations.        |
| `DELETE` | `/containers/{container_name}`         | Removes a container.                                         |
| `GET`    | `/registry`                            | Lists all configured registries.                             |
| `POST`   | `/registry`                            | Adds credentials for a new registry.                         |
| `DELETE` | `/registry/{registry_name}`            | Removes a registry.                                          |

## 🤝 Contributing

Contributions are highly welcome! Feel free to open an *issue* to report bugs or suggest new features. If you'd like to contribute code, please open a *Pull Request*.

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🗺️ Future Roadmap

Here are some of the features and improvements planned for the future of the project:

-   **Local Registry Management**:
    -   Create a private local registry using the `registry:2` image with authentication.
    -   **Automatic Image Updates**:
        -   Detect when a new image is pushed to a registry.
        -   For containers configured to `always pull` the image, automatically update them when a new version becomes available.
-   **Onboarding and User Management**:
    -   Create an installation endpoint (`/install`) for initial setup.
    -   Allow the creation of a `root` user and password on the first run.
    -   Implement a full CRUD for user management.
-   **Multi-Node Support**:
    -   Add the ability to manage resources (CPU, GPU, Memory) across different nodes from a single API.
-   **Webhook System**:
    -   Implement a CRUD system for webhooks, allowing the API to notify external systems about events (e.g., container created, updated, etc.).
-   **Generative AI Interface**:
    -   Develop a view or interactive CLI that uses generative AI to simplify container and configuration creation, reducing the need to manually create JSON files.    

## 🙏 Acknowledgments

A special thanks to my friend, [Paulo Ribeiro](https://github.com/phr-X), for his invaluable guidance and support in this project.