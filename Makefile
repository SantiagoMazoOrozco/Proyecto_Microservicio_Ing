# Makefile for common development tasks

.PHONY: up smoke logs build down

# Start (rebuild) full stack using docker compose (uses docker-compose.yml at repo root)
up:
	docker compose up --build -d

# Run the smoke tests script (creates logs/<timestamp>/)
smoke:
	chmod +x ./scripts/smoke.sh || true
	./scripts/smoke.sh

# Tail logs for core services
logs:
	docker compose logs --tail 200 --no-color ms_seguridad ms_consulta ms_auditoria ms_notificaciones ms_reportes celery_reportes redis mongo mysql

# Stop and remove containers
down:
	docker compose down
