FROM python:3.12-slim

# Set a working directory
WORKDIR /app

# Install system deps (minimal) and pip
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app sources
COPY . /app

EXPOSE 5003

ENV PORT=5003

CMD ["python", "app.py"]
