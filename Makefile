.PHONY: \
	lint-files check-lint \
	setup-environment rebuild-images-and-setup-environment \
	turn-down-environment turn-down-environment-and-destroy-volumes \
	run run-local run-prod backend-run \
	run-tests test \
	init-pkgs clean freeze lint

## ----------------------------
## Execução da API
## ----------------------------

# Execução padrão (mantida)
run:
	PYTHONPATH=./src python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Executa a API local com CORS liberado e ENV=local
run-local:
	ENVIRONMENT=local \
	ORIGINS='["http://localhost:3000","http://127.0.0.1:3000","https://elysium-fronted.vercel.app"]' \
	PYTHONPATH=./src python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Executa a API em modo produção (por exemplo, no servidor)
run-prod:
	ENVIRONMENT=production \
	PYTHONPATH=./src python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Executa a API no modo docker (porta 8100)
backend-run:
	PYTHONPATH=$$(pwd) uvicorn main:app --reload --port 8100

## ----------------------------
## Lint e Qualidade de Código
## ----------------------------

# Formata código com isort e black
lint-files:
	python3 -m isort --profile black .
	python3 -m black -t py312 --line-length 120 --exclude venv .

# Apenas verifica estilo (sem modificar arquivos)
check-lint:
	python3 -m isort --profile black --check-only --diff .
	python3 -m black -t py312 --line-length 120 --check .
	python3 -m flake8 .

# Lint básico do projeto (herdado do primeiro Makefile)
lint:
	flake8 src --exclude=__init__.py

## ----------------------------
## Docker Dev Environment
## ----------------------------

setup-environment:
	docker compose -f docker-compose.dev.yaml up -d

rebuild-images-and-setup-environment:
	docker compose -f docker-compose.dev.yaml up -d --build

turn-down-environment:
	docker compose -f docker-compose.dev.yaml down

turn-down-environment-and-destroy-volumes:
	docker compose -f docker-compose.dev.yaml down -v

## ----------------------------
## Testes
## ----------------------------

# Roda unittest como no segundo projeto
run-tests:
	python3 -m unittest discover -v -s tests -p 'test*.py'

# Alias para compatibilidade com primeiro Makefile
test:
	PYTHONPATH=./src pytest tests/ -v

## ----------------------------
## Utilitários
## ----------------------------

init-pkgs:
	find src -type d -exec touch {}/__init__.py \;

# Atualiza requirements.txt
freeze:
	pip freeze > requirements.txt

# Limpa caches e __pycache__
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + -o -name "*.pyc" -delete
