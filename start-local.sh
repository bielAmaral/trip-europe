#!/usr/bin/env bash
# Servidor local do roteiro (sem cache, sem service worker).
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8888}"
chmod +x serve-dev.py 2>/dev/null || true
if command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:${PORT}/"
fi
exec python3 serve-dev.py
