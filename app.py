"""
PaperQA2 + Streamlit + Ollama (100% local, custo zero).

Importante:
- Configure llm, summary_llm, agent_llm E enrichment_llm para ollama/...
- Sem agent_llm_config, o PaperQA2 tenta OpenAI (GPT-4o) por padrão.
- Sem enrichment_llm_config, o parser multimodal também tenta OpenAI.
- paper_directory no Settings é ignorado; o caminho certo é agent.index.
- Embeddings usam sentence-transformers (st-*), sem API paga.
"""

from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from paperqa import Docs, Settings
from paperqa.settings import (
    AgentSettings,
    AnswerSettings,
    IndexSettings,
    ParsingSettings,
)

# ---------------------------------------------------------------------------
# Ambiente
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

# Evita fallback acidental para a API paga se a chave existir no shell.
os.environ.pop("OPENAI_API_KEY", None)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "st-multi-qa-MiniLM-L6-cos-v1")


def _path_from_env(key: str, default: str) -> Path:
    raw = Path(os.getenv(key, default))
    return raw if raw.is_absolute() else (ROOT / raw)


PDF_DIR = _path_from_env("PDF_DIR", "./documentos")
PQA_HOME = _path_from_env("PQA_HOME", "./.pqa")

# LiteLLM usa o prefixo "ollama/" + nome do modelo no Ollama
LLM_NAME = f"ollama/{OLLAMA_MODEL}"

PDF_DIR.mkdir(parents=True, exist_ok=True)
PQA_HOME.mkdir(parents=True, exist_ok=True)
os.environ["PQA_HOME"] = str(PQA_HOME.resolve())


def build_ollama_llm_config(model_name: str, base_url: str) -> dict:
    """Config LiteLLM Router para o Ollama local (obrigatório para evitar OpenAI)."""
    return {
        "model_list": [
            {
                "model_name": model_name,
                "litellm_params": {
                    "model": model_name,
                    "api_base": base_url,
                    "api_type": "ollama",
                    "timeout": 600,
                    "temperature": 0.0,
                },
            }
        ]
    }


def get_settings() -> Settings:
    """Settings PaperQA2 100% locais: Ollama (LLM) + sentence-transformers (embeddings)."""
    llm_config = build_ollama_llm_config(LLM_NAME, OLLAMA_BASE_URL)
    pdf_dir = str(PDF_DIR.resolve())
    index_dir = str((PQA_HOME / "indexes").resolve())

    return Settings(
        llm=LLM_NAME,
        llm_config=llm_config,
        summary_llm=LLM_NAME,
        summary_llm_config=llm_config,
        embedding=EMBEDDING_MODEL,
        agent=AgentSettings(
            agent_llm=LLM_NAME,
            agent_llm_config=llm_config,
            timeout=1800.0,
            index=IndexSettings(
                paper_directory=pdf_dir,
                index_directory=index_dir,
                concurrency=1,
            ),
        ),
        parsing=ParsingSettings(
            # Sem isto, o PaperQA2 enriquece figuras/tabelas com GPT-4o.
            enrichment_llm=LLM_NAME,
            enrichment_llm_config=llm_config,
            multimodal=False,
        ),
        answer=AnswerSettings(
            max_concurrent_requests=1,
        ),
    )


def ollama_status() -> tuple[bool, str]:
    """Checa se o servidor Ollama responde e se o modelo está instalado."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_BASE_URL}/api/tags", timeout=3) as resp:
            payload = json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.URLError as exc:
        return False, f"Ollama inacessível em {OLLAMA_BASE_URL} ({exc.reason})"
    except Exception as exc:  # noqa: BLE001
        return False, f"Falha ao consultar Ollama: {exc}"

    names = []
    for item in payload.get("models", []):
        name = item.get("name") or item.get("model") or ""
        names.append(name)
        if name == OLLAMA_MODEL or name.startswith(f"{OLLAMA_MODEL}:"):
            return True, f"Ollama ok · modelo `{OLLAMA_MODEL}` encontrado"

    if names:
        preview = ", ".join(names[:8])
        return False, (
            f"Ollama ok, mas `{OLLAMA_MODEL}` não está em `ollama list`. "
            f"Instale com: `ollama pull {OLLAMA_MODEL}`. Disponíveis: {preview}"
        )
    return False, "Ollama respondeu, mas nenhum modelo está instalado."


def init_session_state() -> None:
    if "docs" not in st.session_state:
        st.session_state.docs = Docs()
    if "indexed_files" not in st.session_state:
        st.session_state.indexed_files = set()
    if "last_answer" not in st.session_state:
        st.session_state.last_answer = None


async def index_pdf(path: Path, settings: Settings) -> None:
    await st.session_state.docs.aadd(str(path), settings=settings)


async def ask_question(question: str, settings: Settings):
    return await st.session_state.docs.aquery(question, settings=settings)


def run_async(coro):
    """Executa corrotinas no Streamlit sem brigar com o event loop da UI."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    # Streamlit já tem loop: asyncio.run() na mesma thread quebra.
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PaperQA2 — IA local",
    page_icon="📄",
    layout="wide",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "PaperQA2 local (Ollama). Sem OpenAI. Perguntas só sobre os PDFs enviados.",
    },
)

init_session_state()
settings = get_settings()
ollama_ok, ollama_msg = ollama_status()

st.title("PaperQA2 — IA Local (Ollama)")
st.caption(
    f"Modelo: `{OLLAMA_MODEL}` · Embeddings: `{EMBEDDING_MODEL}` · "
    f"Ollama: `{OLLAMA_BASE_URL}`"
)

if ollama_ok:
    st.success(ollama_msg)
else:
    st.error(ollama_msg)

with st.sidebar:
    st.header("Configuração")
    st.markdown(
        f"""
        - **LLM / summary / agent / enrichment**: `{LLM_NAME}`
        - **Embeddings**: local (`st-*`)
        - **PDFs**: `{PDF_DIR}`
        - **PQA_HOME**: `{PQA_HOME}`

        Troque o modelo no arquivo `.env` (`OLLAMA_MODEL`) para
        `qwen3.5:4b` ou `qwen3.5:2b` se estiver lento demais.
        """
    )
    st.warning(
        "A primeira resposta pode levar alguns minutos (carga do modelo). "
        "Não feche a aba. Isso é normal em PC local."
    )
    if st.button("Limpar Sessão", type="secondary", use_container_width=True):
        st.session_state.docs = Docs()
        st.session_state.indexed_files = set()
        st.session_state.last_answer = None
        st.success("Sessão limpa.")
        st.rerun()

# --- Enviar PDFs ---
st.subheader("1. Enviar PDFs")
uploaded = st.file_uploader(
    "Selecione um ou mais PDFs",
    type=["pdf"],
    accept_multiple_files=True,
    help="Apenas arquivos PDF. Cada um é lido e indexado nesta sessão.",
)

if uploaded:
    for f in uploaded:
        dest = PDF_DIR / Path(f.name).name
        if f.name in st.session_state.indexed_files:
            st.info(f"Já indexado: {f.name}")
            continue
        dest.write_bytes(f.getbuffer())
        with st.status(
            f"Indexando `{f.name}` com Ollama + embeddings locais… "
            "(pode demorar)",
            expanded=True,
        ) as status:
            st.write("Salvando arquivo…")
            st.write("Extraindo texto e gerando embeddings locais…")
            st.write("Inferindo metadados via modelo Ollama (lento)…")
            try:
                run_async(index_pdf(dest, settings))
                st.session_state.indexed_files.add(f.name)
                status.update(label=f"Indexado: {f.name}", state="complete")
            except Exception as exc:  # noqa: BLE001
                status.update(label=f"Erro ao indexar {f.name}", state="error")
                st.error(f"Falha: {exc}")

if st.session_state.indexed_files:
    st.success(
        "Documentos na sessão: "
        + ", ".join(sorted(st.session_state.indexed_files))
    )
else:
    st.info("Nenhum PDF indexado ainda.")

# --- Pergunta ---
st.subheader("2. Pergunta")
question = st.text_area(
    "Digite sua pergunta sobre os documentos",
    placeholder="Ex.: Quais são as principais conclusões do artigo?",
    height=100,
)

ask_clicked = st.button(
    "Perguntar",
    type="primary",
    disabled=not st.session_state.indexed_files or not question.strip() or not ollama_ok,
)

if ask_clicked:
    with st.status(
        f"Processando com `{OLLAMA_MODEL}` local… "
        "Não feche a aba. Pode levar 1–3 minutos.",
        expanded=True,
    ) as status:
        st.write("Buscando evidências nos chunks indexados…")
        st.write("Gerando resumos contextuais (summary_llm via Ollama)…")
        st.write("Compondo a resposta final com citações…")
        try:
            session = run_async(ask_question(question.strip(), settings))
            st.session_state.last_answer = session
            status.update(label="Resposta pronta", state="complete")
        except Exception as exc:  # noqa: BLE001
            status.update(label="Erro na consulta", state="error")
            st.error(f"Falha: {exc}")
            st.session_state.last_answer = None

# --- Resposta ---
session = st.session_state.last_answer
if session is not None:
    st.subheader("3. Resposta")
    answer_text = getattr(session, "formatted_answer", None) or getattr(
        session, "answer", str(session)
    )
    st.markdown(answer_text)
    with st.expander("Mostrar Fontes", expanded=False):
        contexts = getattr(session, "contexts", None) or []
        if not contexts:
            refs = getattr(session, "references", None)
            if refs:
                st.markdown(refs)
            else:
                st.write("Nenhuma fonte estruturada retornada.")
        else:
            for i, ctx in enumerate(contexts, start=1):
                text = getattr(ctx, "text", None) or getattr(ctx, "context", ctx)
                score = getattr(ctx, "score", None)
                citation = ""
                if hasattr(text, "doc") and getattr(text, "doc", None):
                    citation = getattr(text.doc, "citation", "") or getattr(
                        text.doc, "docname", ""
                    )
                elif hasattr(ctx, "text") and hasattr(ctx.text, "name"):
                    citation = ctx.text.name
                st.markdown(
                    f"**Fonte {i}**"
                    + (f" (relevância: {score})" if score is not None else "")
                )
                if citation:
                    st.caption(citation)
                body = getattr(text, "text", None) if text is not None else None
                st.write(body if body is not None else text)
                st.divider()
