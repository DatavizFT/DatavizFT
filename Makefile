# Makefile pour DatavizFT - Commandes de qualité rapides

# Variables
PYTHON = python
PIP = pip

# Installation
install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements-dev.txt

# Qualité du code
format:
	black backend/ tests/
	ruff check --fix backend/ tests/

lint:
	ruff check backend/ tests/
	mypy backend/

check: lint
	black --check backend/ tests/

# Tests
test:
	pytest

test-cov:
	pytest --cov=backend --cov-report=html

# Analyse du code mort
dead-code:
	vulture backend/ --config vulture.toml

dead-code-strict:
	vulture backend/ --config vulture.toml --min-confidence 90

# Pipeline complet
quality: format lint test dead-code

# Nettoyage
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/

# Pipeline principal
run:
	$(PYTHON) -m backend.main

run-force:
	$(PYTHON) -m backend.main --force

# Aide
help:
	@echo "Commandes disponibles:"
	@echo "  install     - Installe les dépendances"
	@echo "  install-dev - Installe les dépendances de développement" 
	@echo "  format      - Formate le code (black + ruff fix)"
	@echo "  lint        - Vérifie la qualité (ruff + mypy)"
	@echo "  test        - Lance les tests"
	@echo "  quality     - Pipeline qualité complet"
	@echo "  run         - Lance le pipeline principal"
	@echo "  clean       - Nettoie les fichiers temporaires"

.PHONY: install install-dev format lint check test test-cov quality clean run run-force help