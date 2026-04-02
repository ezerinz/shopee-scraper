# Use slim Python
FROM python:3.14-slim

# Set environment variable to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies + Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip \
    fonts-liberation \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 \
    libdbus-1-3 libdrm2 libgbm1 libnspr4 libnss3 \
    libx11-6 libxcomposite1 libxdamage1 libxrandr2 \
    xdg-utils ca-certificates \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome Stable
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install Gunicorn explicitly (if not in requirements.txt)
# RUN pip install gunicorn

# Copy app code
COPY . .

# Expose Flask port
EXPOSE 8080

# Run Gunicorn with 4 workers
CMD ["gunicorn", "main:app"]
