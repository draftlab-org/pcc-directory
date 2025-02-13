# Etapa 1: Build dos assets estáticos com Node.js
FROM node:18 AS static_assets

# Definição de argumentos para variáveis de ambiente
ARG MAP_ASSETS_BASE_URL
ARG MAP_STYLE

# Configuração de variáveis de ambiente
ENV MAP_ASSETS_BASE_URL=$MAP_ASSETS_BASE_URL
ENV MAP_STYLE=$MAP_STYLE

# Diretório de trabalho
WORKDIR /app

# Copia apenas package.json e package-lock.json para evitar reinstalações desnecessárias
COPY package*.json ./

# Instala dependências
RUN npm install && npm cache clean --force

# Copia os arquivos restantes
COPY . ./

# Roda o build (com dotenv-expand desativado para evitar loops)
RUN cross-env DOTENV_CONFIG_DISABLE=true npm run build

---

# Etapa 2: Configuração da aplicação Python
FROM python:3.12.0

# Evita buffering do Python
ENV PYTHONUNBUFFERED 1

# Definição de argumentos para variáveis de ambiente
ARG SECRET_KEY

# Atualização do sistema e instalação de dependências
RUN apt update && \
    apt install -y software-properties-common python3-launchpadlib && \
    add-apt-repository ppa:ubuntugis/ppa --yes && \
    apt install -y build-essential gdal-bin libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências do Python
COPY requirements.txt ./

# Atualiza o pip e instala as dependências
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia os arquivos do projeto para o container
COPY . /app/

# Copia os assets estáticos da etapa Node.js
COPY --from=static_assets /app/maps /app/maps

# Coleta arquivos estáticos do Django
RUN python manage.py collectstatic --no-input --clear

# Expõe a porta 8000
EXPOSE 8000

# Comando de execução do Gunicorn com OpenTelemetry
CMD ["opentelemetry-instrument", "gunicorn", "cmdi.wsgi", "-c", "gunicorn.config.py", "--workers", "2", "--threads", "2", "--reload", "--bind", "0.0.0.0:8000"]

