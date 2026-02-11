FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy requirements
COPY backend/requirements.txt .

# Install dependencies
RUN uv pip install --system -r requirements.txt

# Copy backend code
COPY backend/ .

# Expose port
EXPOSE 8000

# Run command
CMD ["uvicorn", "app.api.api:app", "--host", "0.0.0.0", "--port", "8000"]
