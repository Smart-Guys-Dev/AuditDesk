# ==============================================
# AuditPlus v2.0 - Makefile
# ==============================================
# Comandos úteis para desenvolvimento e deploy

.PHONY: install dev test lint clean build docker run help

# Python
PYTHON = python
PIP = pip
VENV = venv

# Docker
DOCKER = docker
COMPOSE = docker-compose

# ==============================================
# Ajuda
# ==============================================
help:
	@echo "AuditPlus v2.0 - Comandos disponíveis:"
	@echo ""
	@echo "  install     - Instalar dependências de produção"
	@echo "  dev         - Instalar dependências de desenvolvimento"
	@echo "  test        - Executar testes"
	@echo "  lint        - Verificar código com flake8"
	@echo "  clean       - Limpar arquivos temporários"
	@echo "  build       - Build do pacote Python"
	@echo "  docker      - Build da imagem Docker"
	@echo "  run         - Executar aplicação"
	@echo ""

# ==============================================
# Instalação
# ==============================================
install:
	$(PIP) install -r requirements.txt

dev:
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"

# ==============================================
# Testes e Qualidade
# ==============================================
test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	flake8 src/ --max-line-length=100
	black --check src/

format:
	black src/

# ==============================================
# Limpeza
# ==============================================
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage

# ==============================================
# Build
# ==============================================
build:
	$(PYTHON) setup.py sdist bdist_wheel

# ==============================================
# Docker
# ==============================================
docker:
	$(DOCKER) build -t auditplus:latest .

docker-run:
	$(COMPOSE) up -d

docker-stop:
	$(COMPOSE) down

docker-logs:
	$(COMPOSE) logs -f

# ==============================================
# Execução
# ==============================================
run:
	$(PYTHON) main.py

# ==============================================
# Backup
# ==============================================
backup:
	$(PYTHON) scripts/backup.py

# ==============================================
# Reset (cuidado!)
# ==============================================
reset-db:
	rm -f audit_plus.db
	$(PYTHON) main.py --init-db
