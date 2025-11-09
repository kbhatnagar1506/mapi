.PHONY: up down api web seed eval install help

help:
	@echo "AIATL Memory System - Makefile Commands"
	@echo ""
	@echo "  make up      - Start Docker services (Qdrant + Neo4j)"
	@echo "  make down    - Stop Docker services"
	@echo "  make api     - Start FastAPI backend"
	@echo "  make web     - Start Next.js frontend"
	@echo "  make seed    - Seed sample memories"
	@echo "  make eval    - Run quick evaluation"
	@echo "  make install - Install all dependencies"

up:
	docker compose -f dev/docker-compose.yml up -d
	@echo "Waiting for services to start..."
	@sleep 3
	@echo "✓ Qdrant & Neo4j are up"

down:
	docker compose -f dev/docker-compose.yml down

install:
	@echo "Installing backend dependencies..."
	cd apps/api && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd apps/web && pnpm install
	@echo "✓ All dependencies installed"

api:
	cd apps/api && PYTHONPATH=../.. uvicorn main:app --reload --port 8000

web:
	cd apps/web && pnpm dev

seed:
	python3 scripts/seed.py

train:
	python3 scripts/train_mapi_direct.py

compare:
	python3 scripts/compare_systems.py

eval:
	python3 scripts/eval_quick.py

