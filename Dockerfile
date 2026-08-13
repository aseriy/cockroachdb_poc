FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN pip install \
    "dbworkload[postgresql]" \
    psycopg-binary \
    psycopg

RUN mkdir -p /app
COPY Trailers.py /app/

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["dbworkload", "run", "-w", "/app/Trailers.py"]
