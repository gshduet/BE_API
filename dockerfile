FROM python:3.12.1-alpine

WORKDIR /app

RUN apk update && apk add --no-cache \
    gcc \
    postgresql-client \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Asia/Seoul

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --no-create-home appuser
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
