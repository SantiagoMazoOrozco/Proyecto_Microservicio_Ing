Microservicio de Auditoría — Docker instructions

Quick start (build + run with Docker Compose)

1. From the `microservicio_auditoria` folder run:

   docker compose up -d --build

2. Wait a few seconds for Mongo to be ready, then run the smoke test from the host (or inside a venv):

   AUDIT_BASE=http://127.0.0.1:5003 python3 smoke_test.py

3. To stop and remove containers:

   docker compose down

Notes
- The compose file exposes Mongo on `27017` and the service on `5003`.
- The image uses Python 3.12. If you need to run locally without Docker, create a python3.12 venv and install `requirements.txt`.
