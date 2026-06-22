# Hermes Setup

Connect any Hermes client to the StackDeploy stack.

## What it configures

- **LLM**: your free cloud provider (set in Hermes `.env` / `config.yaml`)
- **Search**: `http://<server>:8080` (SearXNG)
- **Browser**: `http://<server>:9222` (Chrome CDP)
- **Honcho memory**: `http://<server>:8081`

## Manual config

If you prefer to edit `~/.hermes/config.yaml` directly:

```yaml
model:
  base_url: https://openrouter.ai/api/v1
  default: <provider-model-id>
  provider: openrouter
  api_key: <OPENROUTER_API_KEY>

web:
  backend: searxng
  searxng_url: http://<SERVER_IP>:8080

browser:
  cdp_url: http://<SERVER_IP>:9222

honcho:
  enabled: true
  base_url: "http://<SERVER_IP>:8081"
  workspace: hermes-main
```

For Obsidian note-taking, set the vault path in Hermes to your local Obsidian directory. No separate service is required — Hermes reads and writes markdown directly.
