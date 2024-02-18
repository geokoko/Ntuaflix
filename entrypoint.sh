#!/bin/bash

echo "Waiting for database to become ready..."
while ! mysqladmin ping -h"db" --silent; do
    sleep 1
done
echo "Database is ready."

echo "Checking if database is initialized...(currently running entrypoint)"

python /app/back-end/db/data/database_init.py
# This will wait for the database to be ready before starting the application
exec uvicorn back-end.api.main:app --host 0.0.0.0 --port 9876 --ssl-keyfile /certs/localhost.key --ssl-certfile /certs/localhost.crt
```
