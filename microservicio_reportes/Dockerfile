FROM python:3.11-slim

WORKDIR /app

# Install system deps required to build some Python packages (pycairo, pillow, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       pkg-config \
       libcairo2-dev \
       libgirepository1.0-dev \
       libjpeg-dev \
       zlib1g-dev \
       libfreetype6-dev \
       libpng-dev \
       libffi-dev \
       gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel meson
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

ENV FLASK_RUN_PORT=5002
EXPOSE 5002

CMD ["python", "app.py"]
