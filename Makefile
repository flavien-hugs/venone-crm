MANAGE := FLASK_APP=runserver.py

ifneq (,$(wildcard ./.flaskenv))
    include ./.flaskenv
    export
endif

.PHONY: help
help: ## Show this help
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install or update dependencies
	pip install -r env/dev.txt

initdb: ## Init and create database
	$(MANAGE) flask db init && $(MANAGE) flask init_db

celery-start: ## start celery
	celery -A src.celery worker -B -E --loglevel=INFO

celery-flower: ## start celery
	celery -A src.celery flower --port=5050

migrate: ## Generate an migration
	$(MANAGE) flask db migrate -m 'Intial Migration'

upgrade: ## Apply the upgrade to the database
	$(MANAGE) flask db upgrade

test: ## Run the unit tests
	python3 -m unittest discover -s tests

coverage: ## Run the coverage
	coverage run -m unittest discover

cov-report: ## Generate a code coverage report
	coverage report -m

cov-html: ## Generate an HTML report
	coverage html

shell: ## Flask Shell Load
	$(MANAGE) flask shell

.PHONY: run
run: ## Run
	docker compose up --build -d

.PHONY: restart
restart:	## restart one/all containers
	docker compose restart $(s)

.PHONY: docker-migrate-db
docker-migrate-db: ## Docker migrate db
	docker compose exec web.crm.io FLASK_APP=runserver.py flask init_db

.PHONY: logs
logs: ## View logs from one/all containers
	docker compose logs -f $(s)

.PHONY: down
down: ## Stop the services, remove containers and networks
	docker compose down

.PHONY: destroy-all
destroy-all: ## destroy one/all images
	docker rmi -f $(docker images -a -q)

.PHONY: kill-process
kill-process: ## Kill process the server
	sudo lsof -t -i tcp:5000 | xargs kill -9
