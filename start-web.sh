#!/bin/bash 

PORT=${PORT:-8000}

gunicorn --worker-tmp-dir /dev/shm \
  -k uvicorn.workers.UvicornWorker src.web.main:app \
  --bind "0.0.0.0:${PORT}" \
  -t 200
