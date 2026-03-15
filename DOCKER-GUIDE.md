# Running Agent Second Brain as a Gemini CLI Extension on Docker

This guide explains how to deploy and use the **Agent Second Brain** extension within a Docker environment using the Gemini CLI.

## Architecture Overview

When used as a Gemini CLI extension, the original VPS-based bot architecture is "compressed" into a set of specialized agent skills:

1.  **Gemini CLI**: Acts as the primary orchestrator.
2.  **Extension (`agent-second-brain`)**: Provides the instructional context and tools.
3.  **Specialized Skills**:
    *   `/dbrain-processor`: The core logic that transcribes, classifies, and saves entries.
    *   `/agent-memory`: Manages the Ebbinghaus forgetting curve for your notes.
    *   `/vault-health`: Audits your vault and fixes broken links.
4.  **MCP Server**: Uses `mcp-cli` to connect Todoist tools directly to Gemini.
5.  **Vault**: A local directory inside your Docker container containing your Obsidian Markdown files.

---

## Setup Instructions

### 1. Prerequisites
Ensure your Docker container has the following installed:
- **Node.js (v18+)**
- **Gemini CLI** (`npm install -g @google/gemini-cli`)
- **Git**
- **Python 3.12** (required for memory and graph scripts)

### 2. Link the Extension
Navigate to your project root and link the extension:
```bash
gemini extensions link /path/to/agent-second-brain
```

### 3. Configure Environment Variables
Copy the example environment file and fill in your API keys:
```bash
cp .env.example .env
```
Ensure you provide:
- `TELEGRAM_BOT_TOKEN`: (Optional if running headless, but recommended for capturing entries).
- `TODOIST_API_KEY`: For task management.
- `DEEPGRAM_API_KEY`: For voice transcription.
- `VAULT_PATH`: Point this to your `/vault` directory.

### 4. Setup Todoist MCP
Add the Todoist MCP server to your Gemini CLI configuration:
```bash
gemini mcp add todoist npx -y @modelcontextprotocol/server-todoist --env TODOIST_API_KEY=$TODOIST_API_KEY
```

---

## Execution Workflow

### Manual Processing
You can trigger the brain processing manually from your terminal:
```bash
gemini "/dbrain-processor process today's entries"
```

### Automated Processing (Cron)
To keep your vault healthy and your memory decaying correctly, set up a crontab inside your container:

```bash
# Process entries daily at 21:00
0 21 * * * gemini "/dbrain-processor"

# Run memory decay daily at 23:00
0 23 * * * gemini "/agent-memory decay"

# Build graph and MOCs every Sunday
0 0 * * 0 gemini "/vault-health regenerate MOC"
```

---

## Key Slash Commands

Once linked, these become available in your Gemini CLI session:

- `/dbrain-processor`: Classifies daily notes and creates tasks.
- `/agent-memory`: Manages tiered search and forgetting.
- `/vault-health`: Scores your vault quality (0-100).
- `/graph-builder`: Builds semantic links between orphan notes.
- `/todoist-ai`: Direct task management.

## Docker Optimization Tips

1.  **Persistent Volumes**: Ensure your `vault/` directory is mounted as a Docker volume so your notes survive container restarts.
2.  **Headless Mode**: Use `gemini "command" --approval-mode=yolo` for automated cron jobs to prevent the CLI from waiting for manual confirmations.
3.  **Logs**: Redirect output to a log file for auditing:
    ```bash
    gemini "/dbrain-processor" >> /var/log/second-brain.log 2>&1
    ```
