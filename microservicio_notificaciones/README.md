Microservicio de Notificaciones
================================

Este microservicio expone un API mínimo para crear notificaciones (email) y verificar su estado.

Endpoints
- GET /health -> salud del servicio
- POST /notifications -> crear una notificación. JSON esperado:
  - type: "email"
  - to: destinatario
  - subject: asunto
  - body: contenido
  - async: true|false (si true y hay Celery configurado, se encola)
- GET /notifications/<id>/status -> devuelve metadata y estado

Envío de email
- El envio síncrono usa SMTP configurado por variables de entorno:
  - NOTIFICATIONS_SMTP_HOST
  - NOTIFICATIONS_SMTP_PORT
  - NOTIFICATIONS_SMTP_USER
  - NOTIFICATIONS_SMTP_PASS
  - NOTIFICATIONS_FROM

Soporte asíncrono (opcional)
- Si configuras `CELERY_BROKER_URL` (por ejemplo `redis://redis:6379/0`) y tienes Celery instalado, el servicio encolará con Celery.

Probar localmente
1. Exporta variables necesarias, por ejemplo:

```bash
export NOTIFICATIONS_SMTP_HOST=smtp.example.com
export NOTIFICATIONS_SMTP_PORT=587
export NOTIFICATIONS_SMTP_USER=miusuario
export NOTIFICATIONS_SMTP_PASS=miclave
export NOTIFICATIONS_FROM=no-reply@example.com
```

2. Instala dependencias e inicia la app:

```bash
python -m pip install -r requirements.txt
python app.py
```

3. Ejecuta `smoke_test.py` (opcional):

```bash
python smoke_test.py
```

Microservicio de Notificaciones
================================

Este microservicio expone un API mínimo para crear notificaciones (email) y verificar su estado.

Endpoints
- GET /health -> salud del servicio
- POST /notifications -> crear una notificación. JSON esperado:
  - type: "email"
  - to: destinatario
  - subject: asunto
  - body: contenido
  - async: true|false (si true y hay Celery configurado, se encola)
- GET /notifications/<id>/status -> devuelve metadata y estado

Envío de email
- El envio síncrono usa SMTP configurado por variables de entorno:
  - NOTIFICATIONS_SMTP_HOST
  - NOTIFICATIONS_SMTP_PORT
  - NOTIFICATIONS_SMTP_USER
  - NOTIFICATIONS_SMTP_PASS
  - NOTIFICATIONS_FROM

Soporte asíncrono (opcional)
- Si configuras `CELERY_BROKER_URL` (por ejemplo `redis://redis:6379/0`) y tienes Celery instalado, el servicio encolará con Celery.

Probar localmente
1. Copia el archivo de ejemplo y edítalo:

```bash
cp .env.example .env
# edita .env con tus valores
```

2. Instala dependencias:

```bash
python -m pip install -r requirements.txt
```

3. Run locally (dev):

```bash
export FLASK_APP=microservicio_notificaciones.app
flask run --host=0.0.0.0 --port=5003
```

4. Ejecuta `smoke_test.py` (opcional):

```bash
python smoke_test.py
```

Ejecutar con Docker Compose (recomendado para pruebas de integración con Celery y MailHog)

```bash
docker compose up --build
```

MailHog UI estará en http://localhost:8025 y el servidor SMTP en localhost:1025.

Para correr el worker de Celery (sin docker-compose):

```bash
export CELERY_BROKER_URL=redis://localhost:6379/0
celery -A microservicio_notificaciones.tasks.celery worker --loglevel=info
```

Ejecutar tests (pytest):

```bash
pytest -q
```

Almacenamiento local
- Metadatos de cada notificación se guardan en `notifications/<id>.meta.json` para facilitar verificación manual.
