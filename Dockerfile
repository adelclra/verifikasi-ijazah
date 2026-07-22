FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input 2>/dev/null || true

EXPOSE 8000


CMD ["gunicorn", "verifikasi_ijazah.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "1"]