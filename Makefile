.PHONY: up down build rebuild logs backend-logs frontend-logs seed simulate index smoke status git-status

up:
	docker compose up

build:
	docker compose up --build

rebuild:
	docker compose down
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

backend-logs:
	docker compose logs -f backend

frontend-logs:
	docker compose logs -f frontend

seed:
	curl -X POST "http://localhost:8000/seed/sample-data?force=true"

simulate:
	curl -X POST "http://localhost:8000/simulate/batch?count=50"

index:
	curl -X POST "http://localhost:8000/index/transactions?limit=500"

status:
	curl http://localhost:8000/system/status

smoke:
	./scripts/smoke_test.sh

git-status:
	git status
