#!/usr/bin/env bash
# Instala o AcervoQA no Ubuntu (notebook da apresentação)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "== AcervoQA · instalação Ubuntu =="
echo "Pasta: $PROJECT_ROOT"

if ! command -v python3 &> /dev/null; then
    echo "ERRO: python3 não encontrado."
    echo "Instale com: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual (.venv)..."
    python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip

echo "Instalando PyTorch CPU..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo "Instalando PaperQA + Streamlit..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Criado .env a partir de .env.example"
fi

echo ""
echo "Pronto. Agora:"
echo "  1. Instale o Ollama: curl -fsSL https://ollama.com/install.sh | sh"
echo "  2. Baixe o modelo: ollama pull qwen3.5:4b"
echo "  3. Edite o .env: CONTACT_EMAIL=seu.email@exemplo.com"
echo "  4. Rode: bash scripts/rodar-ubuntu.sh"
echo ""
