# Como Usar a Docker API

Este diretório contém um exemplo de `docker-compose.yml` para executar a `docker-api` em um servidor de produção ou em qualquer outra máquina.

## Pré-requisitos

1.  **Imagem no Docker Hub**: Certifique-se de que o seu workflow do GitHub Actions já executou com sucesso e publicou a imagem no seu repositório do Docker Hub.
2.  **Docker e Docker Compose**: A máquina host precisa ter o Docker e o Docker Compose instalados.

## Passos para Executar

1.  **Crie o Diretório de Projetos**: No mesmo local onde você salvou este `docker-compose.yml`, crie um diretório chamado `docker-projects`.
    ```bash
    mkdir docker-projects
    ```
    É neste diretório que a API irá salvar os arquivos `docker-compose.yml` dos serviços que você criar através dela.

2.  **Verifique a Imagem e o Token**:
    *   Abra o arquivo `docker-compose.yml`.
    *   Na linha `image: lucasargate/docker-api:latest`, troque `lucasargate` pelo **seu nome de usuário** do Docker Hub.
    *   Na seção `environment`, você pode alterar o valor de `PUBLIC_API_KEY` para um token de sua preferência.

3.  **Inicie o Serviço**: Execute o comando abaixo para baixar a imagem e iniciar o contêiner.
    ```bash
    docker compose up -d
    ```

4.  **Verifique se está funcionando**: A API deverá estar acessível em `http://<ip-do-seu-servidor>:5001`. Você pode testar com um comando `curl`:
    ```bash
    # Lembre-se de usar o token que você definiu no docker-compose.yml
    curl -X GET http://localhost:5001/containers \
      -H "Authorization: Bearer dkrapi-pub-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4"
    ```

Agora sua API está pronta para receber chamadas e gerenciar seus outros contêineres!