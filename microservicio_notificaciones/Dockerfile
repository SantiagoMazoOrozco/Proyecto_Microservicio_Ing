FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy
COPY . /app

# Install python deps
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5003

# Use the included Flask development runner by default so the container works
# even if gunicorn isn't installed. For production you can change this to
# gunicorn in requirements or alter the command in compose.
CMD ["python", "app.py"]
