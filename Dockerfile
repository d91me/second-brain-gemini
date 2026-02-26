FROM python:3.12-slim

# Install system dependencies and Node.js
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
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

# Copy dependency files first to leverage Docker cache
COPY pyproject.toml .

# Install Python dependencies using uv
# --no-dev flag is used because this is an environment meant for production bot
RUN uv pip install --system .

# Copy the application code
COPY . .

# Ensure the Gemini settings directory exists and copy settings
# We will use an entrypoint script to substitute variables if needed, 
# or just copy the template if dynamic substitution isn't strictly required by Gemini.
RUN mkdir -p /root/.gemini
COPY .gemini/settings.json /root/.gemini/settings.json

# Ensure vault directory exists (it should be mounted as a volume in Coolify)
RUN mkdir -p /app/vault

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the bot
CMD ["python", "-m", "d_brain"]
