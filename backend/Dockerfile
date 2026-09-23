FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Install ML serving frameworks (CPU versions)
RUN pip install --no-cache-dir scikit-learn xgboost
# PyTorch CPU & TensorFlow CPU can be installed or pulled when building full image
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch

# Copy application packages
COPY backend /app/backend
COPY inference /app/inference

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
