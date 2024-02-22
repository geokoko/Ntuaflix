# Back-end

To connect to the database, create a .env file in the project directory, adding values to the variables below according to your credentials.

- DB_HOST = db (if Docker is used, else add your hostname)
- DB_NAME
- DB_USER
- DB_PASSWD

Fill in your credentials according to your local database settings.

For admin authentication when trying to access the admin routes, add to your .env file:
- ADMIN_USERNAME
- ADMIN_PASSWORD

Fill in your credentials and use them everytime you need to gain admin access at the website. (When trying to access admin endpoints these credentials will be required by your browser).

Finally, export the env variables to your system.

eg.
For Linux:
```bash
export ADMIN_USERNAME=your_admin_username
```

For Windows Command Prompt:
```bash
set ADMIN_USERNAME=your_admin_username
```

For Windows PowerShell:
```bash
$env:ADMIN_USERNAME="your_admin_username"
```
The database is created and populated automatically with the default data during app startup.
To run the app, run: ``uvicorn api.main:app --reload --host 127.0.0.1 --port 9876`` from the /back-end directory.

