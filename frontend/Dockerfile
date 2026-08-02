FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# The application code will be mounted as a volume in development
# The entrypoint command is handled by docker-compose for hot reload
