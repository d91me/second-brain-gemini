#!/bin/bash
set -e

# Generate Xray config if VLESS_URL is provided, and start proxy
if [ -n "$VLESS_URL" ]; then
    echo "⚙️ VLESS_URL provided. Generating Xray config..."
    python scripts/generate_xray_config.py
    if [ -f "/app/xray_config.json" ]; then
        echo "🚀 Starting local Xray proxy..."
        /usr/local/bin/xray-core/xray -c /app/xray_config.json &
        # Give xray a second to start
        sleep 2
        # Export proxy settings for python and child processes
        export HTTP_PROXY="http://127.0.0.1:10809"
        export HTTPS_PROXY="http://127.0.0.1:10809"
        export ALL_PROXY="http://127.0.0.1:10809"
        echo "✅ Proxy enabled (HTTPS_PROXY=$HTTPS_PROXY)"
    else
        echo "⚠️ Failed to generate Xray config."
    fi
fi

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
