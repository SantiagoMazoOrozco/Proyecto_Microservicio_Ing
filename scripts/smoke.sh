#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/smoke.sh
# This script must be run from the repository root on the developer machine.
# It rebuilds the docker-compose stack, waits for services and runs simple health checks.

COMPOSE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$COMPOSE_DIR/docker-compose.yml"

# Logs directory (timestamped)
TS=$(date +%Y%m%dT%H%M%S)
LOG_DIR="$COMPOSE_DIR/logs/$TS"
mkdir -p "$LOG_DIR"

DIAG_FILE="$LOG_DIR/diagnostics.txt"
echo "Smoke run: $TS" > "$DIAG_FILE"
echo "Compose file: $COMPOSE_FILE" >> "$DIAG_FILE"

echo "Using compose file: $COMPOSE_FILE"

# Rebuild and start
docker compose -f "$COMPOSE_FILE" --project-directory "$COMPOSE_DIR" up --build -d

# Wait briefly for services to start
echo "Waiting 8s for services to start..."
sleep 8

echo "---- docker compose ps ----"
# Show status
echo "---- docker compose ps ----" | tee -a "$DIAG_FILE"
docker compose -f "$COMPOSE_FILE" --project-directory "$COMPOSE_DIR" ps | tee -a "$DIAG_FILE"

# Collect recent logs for core services
echo "---- Recent logs (tail 200) ----" | tee -a "$DIAG_FILE"
docker compose -f "$COMPOSE_FILE" --project-directory "$COMPOSE_DIR" logs --tail 200 --no-color ms_seguridad ms_consulta ms_auditoria ms_notificaciones ms_reportes celery_reportes redis mongo mysql --no-color > "$LOG_DIR/compose_logs.txt" || true
echo "Saved compose logs to $LOG_DIR/compose_logs.txt" | tee -a "$DIAG_FILE"

# Also save per-service recent logs for quicker inspection
for svc in ms_seguridad ms_consulta ms_auditoria ms_notificaciones ms_reportes celery_reportes redis mongo mysql; do
  out="$LOG_DIR/${svc}.log"
  docker compose -f "$COMPOSE_FILE" --project-directory "$COMPOSE_DIR" logs --tail 500 --no-color "$svc" > "$out" || true
  echo "Saved $svc logs -> $out" | tee -a "$DIAG_FILE"
done

# Health checks via host mapped ports
echo "---- HTTP health checks (host ports) ----"
check() {
  local url="$1"
  echo -n "Checking $url: " | tee -a "$DIAG_FILE"
  if curl -fsS --max-time 5 "$url" >/dev/null 2>&1; then
    echo "OK" | tee -a "$DIAG_FILE"
    return 0
  else
    echo "FAILED" | tee -a "$DIAG_FILE"
    return 1
  fi
}

echo "---- HTTP health checks (host ports) ----" | tee -a "$DIAG_FILE"
check http://localhost:8000/ || true
check http://localhost:8001/health/ || true
check http://localhost:5003/health || check http://localhost:5003/ || true
check http://localhost:5002/health || check http://localhost:5002/ || true
check http://localhost:5004/health || check http://localhost:5004/ || true

echo "Health checks summary written to $DIAG_FILE"

# Optional: attempt to send a Celery test task to reports worker
read -p "Send a Celery test task to ms_reportes? [y/N] " send_task
if [[ "$send_task" =~ ^[Yy]$ ]]; then
  echo "Sending Celery test task (generate_report_async) inside ms_reportes container..." | tee -a "$DIAG_FILE"
  TASK_OUT="$LOG_DIR/send_task.out"
  if docker compose -f "$COMPOSE_FILE" --project-directory "$COMPOSE_DIR" exec -T ms_reportes python -c "from tasks import generate_report_async; r=generate_report_async.delay('smoke-report', {'test':'smoke'}); print('task_id', r.id)" > "$TASK_OUT" 2>&1; then
    echo "Task send output saved to $TASK_OUT" | tee -a "$DIAG_FILE"
  else
    echo "Failed to send task (see $TASK_OUT)" | tee -a "$DIAG_FILE"
  fi
  echo "Wait 5s and tail worker logs for the task" | tee -a "$DIAG_FILE"
  sleep 5
  docker compose -f "$COMPOSE_FILE" --project-directory "$COMPOSE_DIR" logs --tail 200 --no-color celery_reportes > "$LOG_DIR/celery_worker_tail.log" || true
  echo "Saved celery worker tail to $LOG_DIR/celery_worker_tail.log" | tee -a "$DIAG_FILE"
fi

echo "Smoke tests finished. Artifacts saved under: $LOG_DIR" | tee -a "$DIAG_FILE"
echo "If any checks failed, inspect $DIAG_FILE and the logs in $LOG_DIR" | tee -a "$DIAG_FILE"
