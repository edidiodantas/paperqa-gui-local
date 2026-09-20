#!/usr/bin/env bash
# Monta o volume ext4 do pendrive (venv, cache HuggingFace, modelos Ollama).
# Necessário porque o pendrive está em exFAT e Python/.venv não funcionam nele.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/config.sh"

if findmnt -n "$MNT" >/dev/null 2>&1; then
  echo "Já montado: $MNT"
  exit 0
fi

if [[ ! -f "$IMG" ]]; then
  echo "Imagem ainda não existe: $IMG"
  echo "Rode primeiro: bash scripts/setup-deepin.sh"
  exit 1
fi

mkdir -p "$MNT"
if [[ "$(id -u)" -eq 0 ]]; then
  mount -o loop "$IMG" "$MNT"
else
  sudo mount -o loop "$IMG" "$MNT"
fi

echo "Montado $IMG em $MNT"
df -h "$MNT"
