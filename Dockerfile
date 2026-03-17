# Use official Python image
FROM python:3.11-slim

# Install system dependencies and Node.js
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node dependencies and build Tailwind
COPY package.json package-lock.json* ./
RUN npm install
COPY tailwind.config.js .
COPY app/static/css/input.css ./app/static/css/input.css
COPY app/templates ./app/templates
RUN npm run build

# Copy the rest of the application
COPY . .

# Expose the port (Coolify usually provides $PORT)
ENV PORT=5000
EXPOSE 5000

# Start command
CMD ["sh", "-c", "flask db upgrade && gunicorn -w 4 -b 0.0.0.0:${PORT} run:app"]
