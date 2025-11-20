Smoke tests for local development

This repository includes a helper script `scripts/smoke.sh` that:

- Rebuilds and starts the docker-compose stack
- Waits a short time for services to come up
- Collects logs for core services and saves them under `logs/<timestamp>/`
- Runs simple HTTP health checks against the host-mapped ports
- Optionally sends a Celery test task to `ms_reportes` and captures worker logs

Quick start

From the repository root:

```bash
# Make the script executable (only needed once)
chmod +x scripts/smoke.sh

# Run via Makefile
make smoke

# Or run the script directly
./scripts/smoke.sh
```

After the run you'll find a timestamped folder under `logs/` with:

- `compose_logs.txt` - combined compose logs
- `<service>.log` - per-service recent logs
- `diagnostics.txt` - a short report with health-check results
- `send_task.out` - (if you chose to send a Celery task)

Notes

- The script assumes your `docker-compose.yml` is in the repository root. If your path differs, edit `scripts/smoke.sh` and update `COMPOSE_DIR`.
- Running the Celery task is optional and may fail if the container lacks dev tools; it's only to validate end-to-end task flow.
