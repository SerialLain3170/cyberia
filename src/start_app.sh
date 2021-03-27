# !/bin/bash

sleep 30

echo "app is starting...!"
exec uvicorn server:app --reload --host "0.0.0.0" --port 8000