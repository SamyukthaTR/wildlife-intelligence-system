FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# The application code will be mounted as a volume in development
# The entrypoint command is handled by docker-compose for hot reload
