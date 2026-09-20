# PaperQA2 GUI Local (Ollama + Streamlit)

Interface gráfica para [PaperQA2](https://github.com/Future-House/paper-qa) usando **somente IA local via Ollama** — custo zero, sem OpenAI.

O **mesmo** `app.py` roda no Windows 11 e no Deepin. Só o jeito de instalar muda.

## MVP para apresentação (Windows + Docker)

Docker **não deixa o LLM mais rápido**. O gargalo é o modelo (CPU/GPU), não o Python. Docker resolve outra coisa: **empacotar o produto** (`docker compose up`) no notebook Windows da empresa, sem venv, sem pendrive exFAT, sem “funciona na minha máquina”.

Para captação / demo em empresa 100% Windows, o caminho recomendado é este.

### No notebook da apresentação (na véspera, não na hora)

1. Instale [Docker Desktop](https://www.docker.com/products/docker-desktop/) (WSL2 ligado).
2. Clone o repo **privado** e suba:

```bat
git clone https://github.com/edidiodantas/paperqa-gui-local.git
cd paperqa-gui-local
docker compose up --build
```

3. Na **primeira** subida o container baixa `qwen3.5:4b` (~3,4 GB) e as imagens. Deixe terminar.
4. Abra http://localhost:8501
5. Ensaie com **um** PDF curto. Grave um vídeo de backup (demo ao vivo de LLM falha).

Pare: `Ctrl+C` ou `docker compose down`. Os modelos ficam no volume Docker (não precisa baixar de novo).

Modelo padrão no Compose: `qwen3.5:4b` (cabe em notebook de 16 GB). Não use 9B na reunião.

GPU NVIDIA no Docker (Linux/WSL2) é extra e frágil em TI corporativa:

```bat
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
```

**Não use Docker nesta máquina Deepin para “testar o produto”** se quiser manter o SSD livre: as imagens vão para `/var/lib/docker` (~vários GB). Construa no Windows da demo.

### O que Docker melhora vs o que não melhora

| Melhora (produto) | Não melhora (performance) |
| --- | --- |
| Um comando no Windows | Tokens/s do Qwen |
| Mesmo ambiente na escola e no investidor | Tempo da 1ª carga (~minutos) |
| Sem Python/Ollama “na mão” | Precisa de RAM (16 GB+) e disco |
| História de LGPD: dados no PC, sem OpenAI | GPU antiga / Docker Desktop sem CUDA |

Se o notebook da empresa **bloquear Docker**, o plano B continua sendo Ollama nativo + `streamlit run app.py` (seções Windows abaixo).

## Hardware alvo

- **Windows 11:** i7, 8 GB RAM, RTX ~6 GB VRAM → `qwen3.5:9b` (ou 4b se lento)
- **Deepin 23.1 (este PC):** Ryzen 5 4500, 16 GB RAM, GTX 750 4 GB → use `qwen3.5:4b` (GPU antiga, tende a CPU)
- Alternativa ainda mais leve: `qwen3.5:2b` no `.env`

## Instalar no Deepin 23 (pendrive, sem SSD)

Não instale venv/modelos no SSD nem no exFAT nativo. Guia completo: **[INSTALAR-DEEPIN.md](INSTALAR-DEEPIN.md)**.

Quando for a hora:

```bash
cd /media/Edidio/8662-B449/paperqa-gui-local
bash scripts/setup-deepin.sh
bash scripts/rodar-deepin.sh
```

## Por que `llm="ollama/..."` sozinho não basta

O PaperQA2 usa **quatro** papéis de LLM. O padrão de todos é OpenAI GPT-4o:

| Papel | Setting | Uso |
| --- | --- | --- |
| Resposta + metadados | `llm` + `llm_config` | Indexar e responder |
| Resumos de evidência | `summary_llm` + `summary_llm_config` | `gather_evidence` |
| Agente (ferramentas) | `agent.agent_llm` + `agent_llm_config` | Escolher ferramentas |
| Enrichment multimodal | `parsing.enrichment_llm` + `enrichment_llm_config` | Figuras/tabelas |

O README oficial do PaperQA mostra só `llm` e `summary_llm` no exemplo Ollama. Sem `agent_llm`, ele cai no GPT-4o ([#731](https://github.com/Future-House/paper-qa/discussions/731), [#1321](https://github.com/Future-House/paper-qa/issues/1321)). Versões recentes também usam `enrichment_llm` (padrão GPT-4o) se o multimodal estiver ligado.

Este app configura os quatro + `api_base` do Ollama. Embeddings usam `st-*` (sentence-transformers), sem API paga.

**Não defina `OPENAI_API_KEY`.**

## 1. Instalar Ollama

1. Instale: https://ollama.com/download
2. Baixe o modelo:

```bash
ollama pull qwen3.5:9b
```

Teste:

```bash
ollama run qwen3.5:9b "Olá"
```

Deixe o Ollama rodando (`http://localhost:11434`).

No **Deepin / pendrive** pule as seções 2–3 abaixo e use [INSTALAR-DEEPIN.md](INSTALAR-DEEPIN.md).

## 2. Ambiente Python 3.11+ (Windows / disco NTFS ou ext4)

Não crie `.venv` em pendrive **exFAT**. No Windows, clone para o HD/SSD NTFS.

```bash
git clone https://github.com/edidiodantas/paperqa-gui-local.git
cd paperqa-gui-local
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env      # Linux: cp .env.example .env
```

`paper-qa[local,pymupdf]` instala sentence-transformers (embeddings locais) e o parser PDF.

Edite `.env` se quiser trocar o modelo (ex.: `OLLAMA_MODEL=qwen3.5:4b`).

## 3. Rodar a interface

```bash
streamlit run app.py
```

Abra o URL local (geralmente http://localhost:8501).

## Uso

1. Faça upload de PDFs.
2. Aguarde a indexação (status na tela — será lento no 9B).
3. Digite a pergunta e clique em **Perguntar**.
4. Veja a resposta com citações e abra **Mostrar Fontes**.
5. Use **Limpar Sessão** na barra lateral para recomeçar.

## Latência esperada

Com 6 GB VRAM + 8 GB RAM, o 9B força offload. ~2 tokens/s é esperado; uma resposta curta pode levar 1–2 minutos. A UI usa `st.status` para deixar isso explícito.

Se ficar insuportável, no `.env`:

```bash
OLLAMA_MODEL=qwen3.5:4b
```

Depois: `ollama pull qwen3.5:4b`

## Troubleshooting

| Problema | Solução |
| --- | --- |
| Erro pedindo OpenAI / GPT-4o | Confirme `llm`, `summary_llm`, `agent_llm` e `enrichment_llm` + `*_config` apontando para Ollama (já no `app.py`) |
| `Connection refused :11434` | Inicie o Ollama e teste `ollama list` |
| Modelo não encontrado | `ollama pull qwen3.5:9b` (ou o nome no `.env`) |
| Python antigo | Use 3.11+ |
| Embedding lento no 1º run | Download do modelo HuggingFace na 1ª indexação |
| Timeout do agente | O app usa 1800s; se ainda estourar, baixe para `qwen3.5:4b` |

## Arquitetura

- **LLM / summary / agent / enrichment:** Ollama (`ollama/<modelo>` via LiteLLM)
- **Embeddings:** `st-multi-qa-MiniLM-L6-cos-v1` (local)
- **UI:** Streamlit com `st.status` para latência alta
- **Índice:** `agent.index.paper_directory` e `index_directory` (não `Settings.paper_directory`, que o Pydantic ignora)
