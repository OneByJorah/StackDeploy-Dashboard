# Hermes Setup

Connect any Hermes client to the StackDeploy stack.

## What it configures

- **LLM**: your free cloud provider (set in Hermes `.env` / `config.yaml`)
- **Search**: `http://<server>:8080` (SearXNG)
- **Browser**: `http://<server>:9222` (Chrome CDP)
- **Honcho memory**: `http://<server>:8081`
- **Obsidian**: vault path `/home/<user>/ObsidianVault` (or your chosen path)

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

obsidian:
  enabled: true
  vault_path: /home/<user>/ObsidianVault
```

For Obsidian, install the desktop app locally and open the vault folder. Hermes will read and write notes directly through the Obsidian skill.
