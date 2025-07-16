# MUDANÇA AQUI: Trocamos 'buster' por 'bullseye' (Debian 11)
FROM python:3.9-slim-bullseye

# --------------------------------------------------------------------
# O resto do arquivo continua EXATAMENTE IGUAL
# --------------------------------------------------------------------

# Atualiza a lista de pacotes e instala as dependências necessárias
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Cria o diretório para a chave de autenticação do repositório Docker
RUN install -m 0755 -d /etc/apt/keyrings

# Baixa e adiciona a chave GPG oficial do Docker
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN chmod a+r /etc/apt/keyrings/docker.gpg

# Adiciona o repositório oficial do Docker às fontes do APT
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Atualiza a lista de pacotes novamente, agora com o repositório Docker
RUN apt-get update

# Instala o Cliente Docker (CLI) e o plugin do Compose V2
RUN apt-get install -y docker-ce-cli docker-compose-plugin

# --------------------------------------------------------------------
# O resto do nosso Dockerfile continua igual...
# --------------------------------------------------------------------

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["python3", "main.py"]