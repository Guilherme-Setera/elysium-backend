#!/usr/bin/env bash
set -e
export PORT=${PORT:-8080}
echo "ENVIRONMENT=${ENVIRONMENT:-local}"

if [ "$ENVIRONMENT" = "production" ]; then
  exec gunicorn main:app \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:${PORT} \
    --timeout 120 \
    --workers ${WEB_CONCURRENCY:-2}
else
  exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
fi
