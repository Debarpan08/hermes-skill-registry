FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY registry/ ./registry/
COPY web/ ./web/

EXPOSE 8000

CMD ["python", "-m", "registry.main"]
