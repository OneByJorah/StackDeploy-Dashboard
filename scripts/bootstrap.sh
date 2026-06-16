#!/usr/bin/env bash
set -euo pipefail
SERVER="${1:-REPLACE_WITH_YOUR_TAILSCALE_IP}"
HERMES_CONF="${HOME}/.hermes/config.yaml"

mkdir -p "${HOME}/.hermes"
cp -n "${HERMES_CONF}" "${HERMES_CONF}.bak" 2>/dev/null || true

python3 - "${HERMES_CONF}" "${SERVER}" <<'PY'
import sys, pathlib, re
p = pathlib.Path(sys.argv[1])
server = sys.argv[2]
text = p.read_text()
text = re.sub(r"model:\n(?:  .*\n)*", "model:\n  base_url: http://{server}:8082/v1\n  default: Qwen3.5-9B-Coder-Q4_K_M.gguf\n  provider: custom\n  api_key: hermes-local\n".format(server=server), text)
text = re.sub(r"fallback_providers:\n(?:  .*\n)*", "fallback_providers:\n  - api_key: hermes-local\n    base_url: http://{server}:8082/v1\n    default_model: Qwen3.5-9B-Coder-Q4_K_M.gguf\n    provider: openai-compatible\n".format(server=server), text)
if "searxng_url:" in text:
    text = re.sub(r"searxng_url: .*", "searxng_url: http://{server}:8080".format(server=server), text)
else:
    text = re.sub(r"(web:\n(?:  .*\n)*)", lambda m: m.group(1) + "  searxng_url: http://{server}:8080\n".format(server=server), text)
if "cdp_url:" in text:
    text = re.sub(r"cdp_url: .*", "cdp_url: http://{server}:9222", text)
else:
    text = re.sub(r"(browser:\n(?:  .*\n)*)", lambda m: m.group(1) + "  cdp_url: http://{server}:9222\n", text)
if "honcho:" in text:
    text = re.sub(r"honcho:\n(?:  .*\n)*", "honcho:\n  enabled: true\n  base_url: \"http://{server}:8081\"\n  workspace: hermes-main\n".format(server=server), text)
else:
    text += "\nhoncho:\n  enabled: true\n  base_url: \"http://{server}:8081\"\n  workspace: hermes-main\n".format(server=server)
p.write_text(text)
print("OK -> config updated for", server)
PY
echo "Restart Hermes now: hermes restart"
