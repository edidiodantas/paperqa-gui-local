#!/usr/bin/env bash
# Caminhos comuns dos scripts Deepin. Sempre use: source "$(dirname "$0")/config.sh"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMG="${PROJECT_ROOT}/linux-env.img"
MNT="${PROJECT_ROOT}/linux-env"
IMG_SIZE_GB="${LINUX_ENV_GB:-16}"

export PROJECT_ROOT IMG MNT IMG_SIZE_GB
