FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir .

COPY backend/ ./backend/

EXPOSE 7860

CMD ["uvicorn", "backend.src.api.server:app", "--host", "0.0.0.0", "--port", "8080"]