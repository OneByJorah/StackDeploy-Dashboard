#!/usr/bin/env bash
set -euo pipefail
SERVER="${1:-REPLACE_WITH_YOUR_MESH_VPN_IP}"
printf "server=%s\n" "$SERVER"
printf "llama.cpp: "; curl -s -o /dev/null -w "%{http_code}" "http://$SERVER:8082/v1/models"; echo
printf "SearXNG:   "; curl -sG -o /dev/null -w "%{http_code}" "http://$SERVER:8080/search" -d "q=test&format=json"; echo
printf "Qdrant:    "; curl -s -o /dev/null -w "%{http_code}" "http://$SERVER:6333/healthz"; echo
printf "Chrome:    "; curl -s -o /dev/null -w "%{http_code}" "http://$SERVER:9222/json/version"; echo
printf "Dashboard: "; curl -s -o /dev/null -w "%{http_code}" "http://$SERVER:8501/"; echo
