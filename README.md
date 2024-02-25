# NTUAflix

This guide walks you through setting up and running the NTUAflix application using Docker and docker-compose, including a FastAPI backend, MariaDB database, and Nginx as a reverse proxy.

## Prerequisites

- Docker installed on your machine.
- Docker Compose installed on your machine.

## Setup Instructions

1. **Clone the Repository**

    First, clone this repository to your local machine using:

    ```bash
    git clone https://github.com/ntua/softeng23-42.git
    ```

2. **Environment Variables**

    Create a `.env` file in the root directory of the project. This file should contain the necessary environment variables:

    ```.env
    DB_HOST=db
    DB_NAME=mydatabase
    DB_USER=myuser
    DB_PASSWD=mypassword
    ```
    Adjust the values according to your preferences.

3. **Generate the SSL Certificate and Key**
    Create the following folder:
    ```bash
    mkdir -p nginx/certs
    ```
    Run the following command in your terminal to generate the SSL certificate (localhost.crt) and key (localhost.key). These commands create a certificate valid for 365 days:

    ```bash
    openssl req -newkey rsa:2048 -nodes -keyout nginx/certs/localhost.key -x509 -days 365 -out nginx/certs/localhost.crt
    ```
4. **Nginx Configuration**

    Ensure the `nginx/nginx.conf` file is configured to reverse proxy to the FastAPI application. Here's a simple example that proxies requests to the app service:

    ```nginx
    server {
        listen 80;

        location / {
            proxy_pass http://app:9876;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

5. **Running the application**
    Ensure that no service is listening on localhost at port 3306. Then from the root directory of your project, run:
    ```bash
    sudo docker-compose up
    ```
