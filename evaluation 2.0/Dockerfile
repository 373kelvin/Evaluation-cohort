# Evaluation 2.0 — dashboard + 3 FastAPI services behind nginx (Railway-ready)
FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx supervisor curl gettext-base \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default

WORKDIR /app

COPY requirements-docker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker/entrypoint.sh \
    && mkdir -p outputs/b1-artifact-inventory outputs/b2-endpoint-map outputs/b3-test-results outputs/uploads

ENV PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
    CMD /usr/local/bin/eval-healthcheck

ENTRYPOINT ["/app/docker/entrypoint.sh"]
