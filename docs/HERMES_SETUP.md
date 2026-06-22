# Hermes Setup

Connect any Hermes client to the StackDeploy stack.

## One-command bootstrap

```bash
bash <(curl -s http://REPLACE_WITH_YOUR_MESH_VPN_IP:8501/bootstrap.sh)
hermes restart
```

## What it configures

- **LLM**: `http://<server>:11434/v1` (Ollama)
- **Search**: `http://<server>:8080` (SearXNG)
- **Browser**: `http://<server>:9222` (Chrome CDP)
- **Honcho memory**: `http://<server>:8081`

## Manual config

If you prefer to edit `~/.hermes/config.yaml` directly:

```yaml
model:
  base_url: http://REPLACE_WITH_YOUR_MESH_VPN_IP:11434/v1
  default: qwen2.5:4b
  provider: custom
  api_key: hermes-local

web:
  backend: searxng
  searxng_url: http://REPLACE_WITH_YOUR_MESH_VPN_IP:8080

browser:
  cdp_url: http://REPLACE_WITH_YOUR_MESH_VPN_IP:9222

honcho:
  enabled: true
  base_url: "http://REPLACE_WITH_YOUR_MESH_VPN_IP:8081"
  workspace: hermes-main
```

## Obsidian

For the Obsidian skill, point Hermes to your local vault directory (e.g. `/home/<user>/ObsidianVault`). No separate service is required — Hermes reads and writes markdown files directly.
