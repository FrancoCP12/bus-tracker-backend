# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11.9
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Crear el usuario appuser y su carpeta home de una vez
RUN adduser --disabled-password --gecos "" --home /home/appuser appuser

# 2. Instalar dependencias (como root)
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# 3. Copiar el código (como root)
COPY . .

# 4. Darle permisos al usuario sobre la carpeta de la app
# Esto es vital para que Alembic pueda escribir los archivos de migración
RUN chown -R appuser:appuser /app

# 5. Cambiar al usuario para ejecutar la app
USER appuser

EXPOSE 8000

CMD uvicorn 'app.main:app' --host=0.0.0.0 --port=8000
