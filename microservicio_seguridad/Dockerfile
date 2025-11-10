FROM php:8.1-cli-alpine

# dependencias de sistema y extensiones PHP comunes para Laravel
RUN apk add --no-cache --virtual .build-deps $PHPIZE_DEPS zlib-dev libzip-dev libpng-dev libjpeg-turbo-dev freetype-dev icu-dev oniguruma-dev curl git unzip \
 && apk add --no-cache bash coreutils \
 && docker-php-ext-configure gd --with-freetype --with-jpeg \
 && docker-php-ext-install -j$(nproc) pdo_mysql mbstring exif pcntl bcmath zip gd intl opcache \
 && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
 && apk del .build-deps \
 && rm -rf /var/cache/apk/* /tmp/*

WORKDIR /var/www

# permisos (desarrollo)
RUN addgroup -g 1000 app && adduser -D -u 1000 -G app app || true
RUN chown -R app:app /var/www || true

EXPOSE 8000

CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8000"]