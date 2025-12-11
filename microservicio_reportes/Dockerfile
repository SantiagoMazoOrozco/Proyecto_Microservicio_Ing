FROM python:3.11-slim
WORKDIR /app

# Install build dependencies required to compile some wheels (pycairo, pillow, numpy, etc.)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   pkg-config \
	   libcairo2-dev \
	   python3-dev \
	   libffi-dev \
	   meson \
	   ninja-build \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Install Python dependencies (build deps present in same layer)
RUN pip install --no-cache-dir -r requirements.txt

# Optional: remove build tools to reduce final image size
RUN apt-get purge -y --auto-remove build-essential meson ninja-build pkg-config \
	&& rm -rf /var/lib/apt/lists/*

COPY . .
EXPOSE 5003
CMD ["python", "app.py"]
