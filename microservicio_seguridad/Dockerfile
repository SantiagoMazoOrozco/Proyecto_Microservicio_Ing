FROM composer:2 as builder
WORKDIR /app
COPY composer.json composer.lock* ./
RUN composer install --no-dev --no-interaction --prefer-dist || true
COPY . .

FROM php:8.1-apache
COPY --from=builder /app /var/www/html
RUN chown -R www-data:www-data /var/www/html
# Install PHP extensions required by Laravel (PDO MySQL) and enable rewrite
RUN apt-get update \
	&& apt-get install -y --no-install-recommends default-libmysqlclient-dev libzip-dev zlib1g-dev \
	&& docker-php-ext-install pdo pdo_mysql zip \
	&& rm -rf /var/lib/apt/lists/*

# copy custom vhost to serve Laravel from /var/www/html/public and enable rewrite
COPY docker/000-default.conf /etc/apache2/sites-available/000-default.conf
RUN a2enmod rewrite && a2ensite 000-default.conf || true
EXPOSE 80
CMD ["apache2-foreground"]
