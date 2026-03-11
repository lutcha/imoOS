# ImoOS — Developer Makefile
# Usage: make <target>

.PHONY: help up down build test test-isolation lint format security coverage migrate shell logs

PYTHON = python
MANAGE = $(PYTHON) manage.py
DOCKER_COMPOSE = docker-compose -f docker-compose.dev.yml

help:
	@echo "ImoOS Development Commands"
	@echo "========================="
	@echo "  up              Start all services (Docker)"
	@echo "  down            Stop all services"
	@echo "  build           Build Docker images"
	@echo "  shell           Django shell"
	@echo "  migrate         Run all migrations (shared + tenant)"
	@echo "  migrate-shared  Run shared schema migrations only"
	@echo "  test            Run full test suite"
	@echo "  test-isolation  Run tenant isolation tests (CRITICAL)"
	@echo "  coverage        Run tests with coverage report"
	@echo "  lint            Run flake8 + isort check"
	@echo "  format          Auto-format with black + isort"
	@echo "  security        Run bandit + safety security scans"
	@echo "  logs            Tail all service logs"
	@echo "  create-tenant   Create a new tenant (schema=X name=Y domain=Z)"

up:
	$(DOCKER_COMPOSE) up

down:
	$(DOCKER_COMPOSE) down

build:
	$(DOCKER_COMPOSE) build

logs:
	$(DOCKER_COMPOSE) logs -f

shell:
	$(MANAGE) shell_plus

migrate:
	$(MANAGE) migrate_schemas

migrate-shared:
	$(MANAGE) migrate_schemas --shared

create-tenant:
	$(MANAGE) create_tenant --schema=$(schema) --name="$(name)" --domain=$(domain).imos.cv

test:
	pytest --tb=short

test-isolation:
	@echo "Running MANDATORY tenant isolation tests..."
	pytest tests/tenant_isolation/ -v --tb=long
	@echo "Isolation tests passed."

coverage:
	pytest --cov=apps --cov-report=term-missing --cov-report=html --cov-fail-under=80
	@echo "Coverage report: htmlcov/index.html"

lint:
	flake8 apps/ config/ tests/
	isort --check-only apps/ config/ tests/
	black --check apps/ config/ tests/

format:
	black apps/ config/ tests/
	isort apps/ config/ tests/

security:
	bandit -r apps/ -ll -q
	safety check -r requirements/base.txt

backup-schema:
	@echo "Backing up schema: $(schema)"
	pg_dump -h localhost -U imos -n $(schema) imos > backups/$(schema)_$(shell date +%Y%m%d_%H%M%S).sql

.DEFAULT_GOAL := help
