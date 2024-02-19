FROM python:3.10

# Install MySQL client
RUN apt-get update && apt-get install -y default-mysql-client && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the entire project
COPY . /app

RUN ls /app
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install pyarrow

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Run FastAPI application using uvicorn on the specified port
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]



