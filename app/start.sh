#!/bin/sh
cd ..
ENV=dev uvicorn app.server:app --access-log --host 127.0.0.1 --port 8080 --workers 1
