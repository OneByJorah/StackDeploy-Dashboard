#!/usr/bin/env bash
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo '=== Service checks ==='
curl -s -o /dev/null -w 'searxng=%{http_code}\n' 'http://localhost:8080/search?format=json&q=test'
curl -s -o /dev/null -w 'camofox=%{http_code}\n' http://localhost:9377/health
curl -s -o /dev/null -w 'obsidian=%{http_code}\n' http://localhost:8083/
curl -s -o /dev/null -w 'qdrant=%{http_code}\n' http://localhost:6333/

echo '=== SearXNG JSON ==='
curl -s 'http://localhost:8080/search?format=json&q=python&language=en' > /tmp/sd_searxng.json
python3 -c 'import json,sys; d=json.load(open("/tmp/sd_searxng.json")); print("results=", len(d.get("results", [])))'

echo '=== Camofox tab ==='
curl -s -X POST http://localhost:9377/tabs -H 'Content-Type: application/json' -d '{"userId":"sd-test","sessionKey":"default","url":"https://example.com"}' > /tmp/sd_camofox_tab.json
python3 -c 'import json,sys; d=json.load(open("/tmp/sd_camofox_tab.json")); print("tabId=", d.get("tabId")); assert d.get("tabId"), "tabId missing"'

echo '=== CloakBrowser CLI ==='
# Best-effort: requires `cd browser-search && npm install` first.
( cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"/browser-search && node scripts/cloak/cloak-fetch.mjs --help > /dev/null 2>&1 ) \
  && echo "cloak-fetch: ok" || echo "cloak-fetch: skipped (run npm install in browser-search/)"

echo '=== Obsidian page ==='
curl -s http://localhost:8083/ | grep -q 'Obsidian v1.7.7'

echo '=== All done ==='
