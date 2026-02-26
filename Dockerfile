FROM python:3.12-slim

# Install system dependencies and Node.js
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    gettext-base \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Install Gemini CLI globally
RUN npm install -g @google/gemini-cli

# Set working directory
WORKDIR /app

# Copy dependency + source files needed for pip install
COPY pyproject.toml .
COPY src/ src/

# Install Python dependencies using uv
RUN uv pip install --system .

# Copy the rest of the application (entrypoint, vault skeleton, .gemini, docs, etc.)
COPY . .

# Ensure the Gemini settings directory exists
# settings.json template is kept in /app/.gemini/ — envsubst runs at startup
RUN mkdir -p /root/.gemini

# Ensure vault directory exists (it should be mounted as a volume in Coolify)
RUN mkdir -p /app/vault

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set up entrypoint script
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

