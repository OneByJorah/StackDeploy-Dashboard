# Hermes Setup

Connect any Hermes client to the Free Auto Project stack.

## One-command bootstrap

```bash
bash <(curl -s http://REPLACE_WITH_YOUR_MESH_VPN_IP:8501/bootstrap.sh)
hermes restart
```

## What it configures

- **LLM**: `http://<server>:8082/v1`
- **Search**: `http://<server>:8080`
- **Browser**: `http://<server>:9222`
- **Honcho memory**: `http://<server>:8081`

## Manual config

If you prefer to edit `~/.hermes/config.yaml` directly:

```yaml
model:
  base_url: http://REPLACE_WITH_YOUR_MESH_VPN_IP:8082/v1
  default: Qwen3.5-9B-Coder-Q4_K_M.gguf
  provider: custom
  api_key: hermes-local

web:
  searxng_url: http://REPLACE_WITH_YOUR_MESH_VPN_IP:8080

browser:
  cdp_url: http://REPLACE_WITH_YOUR_MESH_VPN_IP:9222

honcho:
  enabled: true
  base_url: "http://REPLACE_WITH_YOUR_MESH_VPN_IP:8081"
  workspace: hermes-main
```
