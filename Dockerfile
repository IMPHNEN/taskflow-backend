# Use Python 3.10 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies and Go
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install chromium and deps for patchright
RUN patchright install --with-deps chromium

# Cleanup
RUN apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
# Copy project files
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["python", "run.py"]