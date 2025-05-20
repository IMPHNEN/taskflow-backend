# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies and Go
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    && wget https://go.dev/dl/go1.24.3.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.24.3.linux-amd64.tar.gz \
    && rm go1.24.3.linux-amd64.tar.gz

# Add Go to PATH
ENV PATH=$PATH:/usr/local/go/bin

# Install github-mcp-server
RUN git clone https://github.com/github/github-mcp-server.git github-mcp-server-git \
    && cd github-mcp-server-git \
    && git checkout 2f8c287 \
    && go mod download \
    && cd cmd/github-mcp-server \
    && go build -o github-mcp-server\
    && mv github-mcp-server /usr/local/bin/ \
    && cd / \
    && rm -rf github-mcp-server-git

# Cleanup: remove Go, git, and wget
RUN rm -rf /usr/local/go \
    && apt-get update \
    && apt-get purge -y git wget \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["python", "run.py"]