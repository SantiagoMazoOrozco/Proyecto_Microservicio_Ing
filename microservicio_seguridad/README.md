# Microservicio Seguridad

Este servicio es una aplicación Laravel (API) usada para la autenticación/seguridad del proyecto.

Contenido rápido
- Laravel 8.x
- PHP 8.1 (Dockerfile usa `php:8.1-cli-alpine`)
- Servicios: MySQL y Redis (definidos en `docker-compose.yml`)

Archivos importantes
- `Dockerfile` — imagen PHP para desarrollo/servicio
- `docker-compose.yml` — define `app`, `db` y `redis`
- `.env.docker` — archivo con variables pensadas para ejecutarlo con Docker Compose
- `phpunit.xml` y `tests/` — pruebas automatizadas

Arrancar localmente (usando Docker Compose)

1. En la carpeta del microservicio:

```bash
cd microservicio_seguridad
# Usa el .env para desarrollo local, o el .env.docker para ejecutar en contenedores
docker-compose --env-file .env.docker up --build -d
```

2. Ver logs o entrar al contenedor `app`:

```bash
docker-compose logs -f
docker-compose exec app sh
```

3. Ejecutar pruebas dentro del contenedor:

```bash
docker-compose exec app ./vendor/bin/phpunit --configuration phpunit.xml
```

Ejecución local sin Docker (si tienes PHP y Composer instalados)

```bash
composer install
# Copiar o ajustar .env según tu entorno
vendor/bin/phpunit --configuration phpunit.xml
```

Notas y recomendaciones
- El `docker-compose.yml` fue actualizado temporalmente para mapear MySQL en el puerto `3307` del host (evitar conflictos con una instancia local en 3306). Ajusta si lo necesitas.
- Para CI se usa SQLite en memoria para pruebas rápidas y reproducibles.