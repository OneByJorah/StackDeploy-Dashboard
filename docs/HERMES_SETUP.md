# Hermes Setup

## Quick start

```bash
git clone https://github.com/OneByJorah/StackDeploy.git
cd StackDeploy
cp .env.example .env
bash scripts/bootstrap.sh
hermes restart
```

## Hermes config

Point Hermes at the free cloud provider of your choice, plus the local services above:

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

For local Obsidian, open the vault folder in the desktop app. Hermes reads and writes notes directly through the Obsidian skill.
