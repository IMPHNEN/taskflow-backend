#!/bin/bash

# Calculate optimal thread count
# WORKER_COUNT=$(($(nproc) * 2 + 1))
WORKER_COUNT=1
THREAD_COUNT=$(( $(nproc) * 2 < 8 ? $(nproc) * 2 : 8 ))

# Run gunicorn with calculated thread count
exec gunicorn --bind 0.0.0.0:8000 --workers $WORKER_COUNT --threads $THREAD_COUNT --worker-class uvicorn.workers.UvicornWorker --timeout 120 app.main:app 