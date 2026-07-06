FROM python:3.11-slim

# Install system dependencies untuk PaddleOCR dan OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements dulu (biar Docker cache layer ini)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy semua kode aplikasi
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input 2>/dev/null || true

# Expose port
EXPOSE 8000

# Start command
CMD ["gunicorn", "verifikasi_ijazah.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "1"]