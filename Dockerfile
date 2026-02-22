# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.10-slim AS builder

WORKDIR /app

# Variables d'environnement pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install pipenv to handle Pipfile
RUN pip install --no-cache-dir pipenv

# Copier uniquement les fichiers de dépendances pour profiter du cache Docker
COPY Pipfile Pipfile.lock ./

# Generate requirements.txt from Pipfile.lock
RUN pipenv requirements > requirements.txt

# Installer les dépendances dans un virtualenv isolé
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt

# ── Runtime stage ───────────────────────────────────────────────────────────────
FROM python:3.10-slim AS runtime

WORKDIR /app

# Install locales and common utilities
RUN apt-get update && apt-get install -y --no-install-recommends locales && \
    sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    VIRTUAL_ENV=/venv \
    LANG=fr_FR.UTF-8 \
    LANGUAGE=fr_FR:fr \
    LC_ALL=fr_FR.UTF-8 \
    FLASK_APP=runserver.py

# Copier uniquement le virtualenv depuis le builder
COPY --from=builder /venv /venv

# Copier le code applicatif
COPY . .

# Least-privilege : permettre l'exécution par un utilisateur non-root
RUN chgrp -R 0 /app && chmod -R g=u /app

# Exposer le port applicatif
EXPOSE 5000

# Démarrer Gunicorn en production (Point d'entrée corrigé: venone_app)
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "runserver:venone_app"]
