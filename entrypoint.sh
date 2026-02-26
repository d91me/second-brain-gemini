#!/bin/bash
set -e

# Substitute environment variables in Gemini settings
# This handles ${TODOIST_API_KEY} placeholder in settings.json
if [ -f /app/.gemini/settings.json ]; then
    envsubst < /app/.gemini/settings.json > /root/.gemini/settings.json
    echo "✅ Gemini settings configured"
fi

# Ensure vault directories exist
mkdir -p /app/vault/daily
mkdir -p /app/vault/attachments
mkdir -p /app/vault/thoughts
mkdir -p /app/vault/summaries
mkdir -p /app/vault/MOC

echo "🚀 Starting d-brain bot..."
exec python -m d_brain
