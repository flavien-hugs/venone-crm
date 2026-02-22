# Variables
MANAGE := FLASK_APP=runserver.py
DOCKER_COMPOSE := docker compose
APP_SERVICE := app

.PHONY: help
help: ## Afficher cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- LOCAL DEVELOPMENT ---

.PHONY: install
install: ## Installer les dépendances (pipenv)
	pipenv install

.PHONY: shell
shell: ## Lancer le shell Flask
	$(MANAGE) flask shell

.PHONY: run
run: ## Lancer le serveur de développement local
	$(MANAGE) flask run

.PHONY: test
test: ## Exécuter les tests unitaires
	pipenv run python3 -m unittest discover -s tests

.PHONY: coverage
coverage: ## Exécuter la couverture de code
	pipenv run coverage run -m unittest discover
	pipenv run coverage report -m

# --- DATABASE (LOCAL) ---

.PHONY: db-init
db-init: ## Initialiser la base de données (migrations + rôles)
	$(MANAGE) flask init-db

.PHONY: db-roles
db-roles: ## Initialiser uniquement les rôles
	$(MANAGE) flask init-roles

.PHONY: db-migrate
db-migrate: ## Générer une nouvelle migration
	$(MANAGE) flask db migrate

.PHONY: db-upgrade
db-upgrade: ## Appliquer les migrations
	$(MANAGE) flask db upgrade

.PHONY: db-drop
db-drop: ## Vider la base de données (supprimer les tables)
	$(MANAGE) flask drop-db

.PHONY: db-seed
db-seed: ## Peupler la base de données avec des données de test
	$(MANAGE) flask seed-db --count 5

.PHONY: admin
admin: ## Créer l'utilisateur administrateur par défaut
	$(MANAGE) flask create-admin

# --- DOCKER ---

.PHONY: up
up: ## Lancer les conteneurs en arrière-plan
	$(DOCKER_COMPOSE) up -d --build

.PHONY: down
down: ## Arrêter les conteneurs
	$(DOCKER_COMPOSE) down --remove-orphans

.PHONY: build
build: ## Reconstruire les images Docker
	$(DOCKER_COMPOSE) build

.PHONY: logs
logs: ## Afficher les logs en temps réel
	$(DOCKER_COMPOSE) logs -f

.PHONY: dk-init
dk-init: ## Initialiser la DB dans Docker
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) flask init-db

.PHONY: dk-roles
dk-roles: ## Initialiser uniquement les rôles dans Docker
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) flask init-roles

.PHONY: dk-admin
dk-admin: ## Créer l'admin dans Docker
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) flask create-admin

.PHONY: dk-seed
dk-seed: ## Seeder la DB dans Docker
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) flask seed-db --count 10

.PHONY: dk-drop
dk-drop: ## Vider la DB dans Docker
	$(DOCKER_COMPOSE) exec $(APP_SERVICE) flask drop-db

# --- CELERY ---

.PHONY: celery-worker
celery-worker: ## Lancer le worker Celery (local)
	celery -A src.celery_worker:celery worker --loglevel=info

.PHONY: celery-flower
celery-flower: ## Lancer Flower pour monitorer Celery
	celery -A src.celery_worker:celery flower --port=5555

# --- UTILS ---

.PHONY: kill-port
kill-port: ## Tuer le processus occupant le port 5000 (Local)
	@echo "Recherche du processus sur le port 5000..."
	@fuser -k 5000/tcp || echo "Aucun processus local trouvé sur 5000."
