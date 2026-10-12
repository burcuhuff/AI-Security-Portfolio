# secure-enterprise-mcp/dockerfile
FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home app \
    && mkdir /app/logs \
    && chown app:app /app/logs

COPY client/ ./client/
COPY server/ ./server/
COPY data/trusted/ ./data/trusted/

USER app

CMD ["python", "-m", "client.agent"]