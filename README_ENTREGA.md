# Segunda entrega – Proyecto de Microservicios

se explica cómo está montado el proyecto, cómo se levantan los contenedores y cómo se prueban las funcionalidades principales de cada microservicio.

---

## 1. Cómo se levanta todo el sistema

1. Primero se entra a la carpeta raíz del proyecto:

   ```bash
   cd "Proyecto Del Curso"
   ```
2. Luego se levantan todos los servicios con Docker Compose. Normalmente se usa el script de smoke porque ya hace el build y algunos checks básicos:

   ```bash
   ./scripts/smoke.sh
   ```

   Si quiero hacerlo a mano, también puedo usar:

   ```bash
   docker compose up -d --build
   ```
3. Para asegurarse de que todo se levantó bien, se revisa el estado de los contenedores:

   ```bash
   docker compose ps
   ```

  Ahí se verifica que todos estén en estado `Up`.

---

## 2. Servicios y puertos que utilizo

Cuando el `docker-compose.yml` está corriendo, tengo estos servicios expuestos en mi máquina local:

- **Seguridad (Laravel)**: `http://localhost:8000/`
- **Consulta (Django)**: `http://localhost:8001/`
  - Endpoint de health: `http://localhost:8001/health/`
- **Auditoría (Flask + Mongo)**: `http://localhost:5003/`
  - Endpoint de health: `http://localhost:5003/health`
- **Reportes (Flask + Celery)**: `http://localhost:5002/`
  - Endpoint de health: `http://localhost:5002/health`
- **Notificaciones (Flask)**: `http://localhost:5004/`
  - Endpoint de health: `http://localhost:5004/health`
- **Mailhog (correo de pruebas)**: `http://localhost:8025/`

Lo primero que se suele hacer al levantar el proyecto es probar los endpoints de salud para ver que todos contesten `HTTP 200`.

---

## 3. Pruebas que hago sobre cada microservicio

### 3.1. Microservicio de Seguridad

Este microservicio se encarga de la autenticación y de emitir el token que usan otros servicios.

**Crear un usuario**

La creación de usuario se prueba con este comando:

```bash
curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"demo","email":"demo@example.com","password":"secret123"}' \
  http://localhost:8000/api/create_user
```

Con esto se debería crear el usuario en la base de datos y recibir un JSON con la información del usuario creado.

**Hacer login y obtener el token**

El login con el mismo usuario se prueba así:

```bash
curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"secret123"}' \
  http://localhost:8000/api/login
```

La respuesta trae un campo `access_token`. Ese valor es el que necesito para probar las rutas protegidas en otros microservicios (por ejemplo, auditoría).

---

### 3.2. Microservicio de Consulta

Este microservicio se usa para las consultas sobre torneos, jugadores, etc.

Primero se revisa el health:

```bash
curl -sS http://localhost:8001/health/
```

#### Ejemplo 1: torneos por país

Se hace una llamada a uno de los endpoints de negocio, por ejemplo el de torneos por país:

```bash
curl -sS "http://localhost:8001/get-tournaments-by-country/?country=Colombia"
```

En este endpoint se ve cómo la API valida los parámetros y trabaja con los datos de torneos.

#### Ejemplo 2: obtener ID de evento a partir de un link de start.gg

También hay un flujo donde, pegando un link de un torneo de start.gg, el microservicio obtiene el ID del evento usando GraphQL.

Por ejemplo, con este enlace:

```text
https://www.start.gg/tournament/climax-2025-the-last-bite/event/smash-bros-ultimate-singles
```

Las partes relevantes del enlace son:

- `climax-2025-the-last-bite` → nombre del torneo (sin las barras).
- `smash-bros-ultimate-singles` → nombre del evento.

Con esas dos partes, el servicio arma la consulta y obtiene el ID del evento.

Para probar ese flujo, se usa el endpoint de obtener ID de evento (la ruta está mapeada en `api_only_urls.py` como `get-event-id/`). Un ejemplo de llamada es:

```bash
curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d '{"tournament_slug":"climax-2025-the-last-bite","event_slug":"smash-bros-ultimate-singles"}' \
  http://localhost:8001/get-event-id/
```

La idea de esta parte es mostrar que, a partir del link del torneo y el evento, el microservicio se encarga de hablar con la API de start.gg y devolver el ID correspondiente.

Con el torneo `climax-2025-the-last-bite` y el evento `smash-bros-ultimate-singles`, la respuesta que se obtiene es, por ejemplo:

```json
{"event_id": 1439491}
```

---

### 3.3. Microservicio de Reportes

Este microservicio genera reportes (por ejemplo, en PDF) a partir de la información.

**Probar el health**

```bash
curl -sS http://localhost:5002/health
```

**Crear un reporte**

Para generar un reporte,  se envía un JSON con los datos básicos del reporte:

```bash
curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d '{"type":"pdf","title":"Demo reporte","content":"Hola reporte"}' \
  http://localhost:5002/reports
```

La respuesta incluye un `id` de reporte y un estado inicial (por ejemplo `pending`).

**Ver los archivos que se generan**

Después, entro al contenedor del microservicio de reportes y reviso la carpeta donde se guardan los archivos:

```bash
docker compose exec -T ms_reportes ls -1 reports
```

En esa carpeta se ven archivos `.pdf` y `.meta.json` correspondientes a los reportes creados. Eso confirma que el microservicio está generando los documentos correctamente.

---

### 3.4. Microservicio de Notificaciones

Este microservicio se encarga de enviar notificaciones (por ejemplo correos de prueba usando Mailhog).

**Health**

```bash
curl -sS http://localhost:5004/health
```

**Enviar una notificación de correo**

Se puede probar con una notificación de tipo `email` en modo síncrono:

```bash
curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d '{"type":"email","to":"test@example.com","subject":"Demo","body":"Hola desde ms_notificaciones","async":false}' \
  http://localhost:5004/notifications
```

La respuesta incluye un `id` de notificación y un `status` (por ejemplo `sent`).

Para revisar el correo de prueba, se abre Mailhog en el navegador:

- `http://localhost:8025`

Ahí puedo ver los correos que ha enviado el microservicio.

---

### 3.5. Microservicio de Auditoría

Este microservicio guarda logs en MongoDB y está protegido por el microservicio de seguridad.

**Health**

```bash
curl -sS http://localhost:5003/health
```

**Probar que está protegido**

Si intento crear un log sin token válido, el servicio responde con error. Por ejemplo:

```bash
curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d '{"level":"info","service":"manual-test","message":"Log desde consola"}' \
  http://localhost:5003/logs
```

La respuesta es algo como:

```json
{"detail":"invalid_token"}
```

Esto muestra que auditoría sí está consultando al microservicio de seguridad y solo acepta peticiones autenticadas.

**(Opcional) Crear un log con token válido**

Si quiero probar el flujo completo:

1. Primero hago login en seguridad y copio el `access_token`.
2. Luego envío el log con el header `Authorization: Bearer <token>`:

   ```bash
   TOKEN="PEGAR_AQUI_EL_ACCESS_TOKEN"

   curl -sS -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"level":"info","service":"manual-test","message":"Log con token valido"}' \
     http://localhost:5003/logs
   ```
3. Después puedo consultar estadísticas:

   ```bash
   curl -sS "http://localhost:5003/stats"
   ```

   Ahí se ve cómo aumenta el contador de logs registrados.

---

## 4. Resumen

En resumen por si no entiendo, se levanta todo el entorno con Docker Compose desde la raíz del proyecto y luego se hacen estas revisiones:

1. Verifico que todos los contenedores estén `Up` (`docker compose ps`).
2. Se hace la comprobacion de los endpoints de `health` de cada microservicio.
3. Pruebo un caso representativo por microservicio:
   - Seguridad: crear usuario y login (token).
   - Consulta: una llamada a la API de torneos.
   - Reportes: crear un reporte y ver el PDF generado en `reports/`.
   - Notificaciones: enviar un correo y verlo en Mailhog.
   - Auditoría: comprobar que sin token responde `invalid_token` y, opcionalmente, probar la creación de logs con un token válido.

Con estos pasos se verifica que la conexión entre contenedores funciona, que los microservicios están vivos y que las funcionalidades principales del proyecto están operativas.
