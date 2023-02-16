MANAGE := FLASK_APP=runserver.py


.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: ## Make a new virtual environment
	pipenv shell

.PHONY: install
install: venv ## Install or update dependencies
	pipenv install

freeze: ## Pin current dependencies
	pipenv requirements > requirements.txt

test: ## Run the unit tests
	$(MANAGE) flask test

initdb: ## Init and create database
	$(MANAGE) flask db init && $(MANAGE) flask init_db

migrate: ## Generate an initial migration
	$(MANAGE) flask db migrate -m 'Intial Migration'

upgrade: ## Apply the upgrade to the database
	$(MANAGE) flask db upgrade

revision: ## Apply the revision to the database
	$(MANAGE) flask db revision --rev-id 2e45b86ed899

heads: ## Apply the heads to the database
	$(MANAGE) flask db stamp heads

merge: ## Apply the merge to the database
	$(MANAGE) flask db merge heads -m "merging two heads"

history: ## Apply the history to the database
	$(MANAGE) flask db history

downgrade: ## Remove the last migration from the database
	$(MANAGE) flask db downgrade

current: ## Shows the current revision of the database.
	$(MANAGE) flask db current

shell: ## Flask Shell Load
	$(MANAGE) flask shell

.PHONY: kill-process
kill-process: ## Kill process the server
	sudo lsof -t -i tcp:5000 | xargs kill -9
