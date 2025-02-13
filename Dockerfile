FROM node:20 AS static_assets

ARG MAP_ASSETS_BASE_URL
ARG MAP_STYLE

ENV MAP_ASSETS_BASE_URL=$MAP_ASSETS_BASE_URL
ENV MAP_STYLE=$MAP_STYLE

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . ./
RUN npm run build


FROM python:3.12.0

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt update && \
    apt install -y --no-install-recommends \
        software-properties-common \
        python3-launchpadlib \
        build-essential \
        gdal-bin \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/
COPY --from=static_assets /app/maps /app/maps

RUN python manage.py collectstatic --no-input --clear

EXPOSE 8000

CMD ["opentelemetry-instrument", "gunicorn", "cmdi.wsgi", "-c", "gunicorn.config.py", "--workers", "2", "--threads", "2", "--reload", "--bind", "0.0.0.0:8000"]



