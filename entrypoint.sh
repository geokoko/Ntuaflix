#!/bin/bash

set -a # automatically export all variables
source .env
set +a

echo "Checking if database is initialized...(currently running entrypoint)"

# Wait for the database service to be ready
until mysql -h "${DB_HOST}" -u "${DB_USER}" -p"${DB_PASSWD}" -e ";" ; do
  >&2 echo "MariaDB is unavailable - sleeping"
  sleep 1
done

DB_EXISTS=$(mysql -h "${DB_HOST}" -u "${DB_USER}" -p"${DB_PASSWD}" -e "SHOW DATABASES LIKE '${DB_NAME}';" | grep "${DB_NAME}" > /dev/null; echo "$?")
DDL_SCRIPT_PATH="back-end/db/ntuaflix_ddl.sql"
# If the database does not exist, run the DDL script
if [[ "${DB_EXISTS}" -ne 0 ]]; then
   echo "Database does not exist. Initializing database..."
   mysql -h "${DB_HOST}" -u "${DB_USER}" -p"${DB_PASSWD}" < "${DDL_SCRIPT_PATH}"
else
  echo "Database exists. Skipping initialization."
fi

# This will wait for the database to be ready before starting the application
exec uvicorn back-end.api.main:app --host 0.0.0.0 --port 9876 --ssl-keyfile /certs/localhost.key --ssl-certfile /certs/localhost.crt
```
