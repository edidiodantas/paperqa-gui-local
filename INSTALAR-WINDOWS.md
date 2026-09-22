# Instalar no Windows 11 (i7 + SSD) a partir do pendrive

Este é o caminho certo para o PC da apresentação: **Python + Ollama nativos no SSD**.  
Não rode o projeto de dentro do pendrive (ele está em exFAT; o `.venv` quebra).

O programa é o **mesmo** do Linux: `app.py` + `academic_search.py` (Oasisbr, SciELO, Unpaywall). Só muda a instalação.

## 0. Copiar para o SSD

No Explorer: copie a pasta **inteira** `paperqa-gui-local` do pendrive para, por exemplo:

`C:\paperqa-gui-local`

Não clone um GitHub antigo: a busca Oasisbr está nesta pasta (`academic_search.py`).  
Não reutilize o `.env` do Deepin (ele aponta para `/media/.../pqa-linux`). O instalador gera um `.env` do Windows.

Abra o **PowerShell** ou **CMD** nessa pasta.

## 1. Python 3.12

1. https://www.python.org/downloads/release/python-31210/ (Windows installer 64-bit)
2. Marque **Add python.exe to PATH**
3. Confira:

```bat
py -3.12 --version
```

Se reclamar de compilação depois (`tantivy` / `torch`), instale [Build Tools C++](https://visualstudio.microsoft.com/visual-cpp-build-tools/) com “Desktop development with C++”. Na prática os wheels costumam bastar.

## 2. Ollama

1. https://ollama.com/download (Windows)
2. Deixe o Ollama aberto (ícone na bandeja). Ele escuta `http://localhost:11434`.
3. No CMD:

```bat
ollama pull qwen3.5:4b
ollama run qwen3.5:4b "Olá"
```

Use **4b** na primeira vez (demo estável). Se o PC tiver placa NVIDIA ~6 GB e a 4b estiver folgada, aí sim teste `qwen3.5:9b`.

Não crie `OPENAI_API_KEY`.

## 3. Ambiente do app

Na pasta `C:\paperqa-gui-local`:

```bat
install-windows.bat
```

Isso cria o `.venv`, instala as libs (incluindo `httpx` da busca) e gera um `.env` Windows com `OLLAMA_MODEL=qwen3.5:4b`.

Edite o `.env` e coloque um **e-mail real da escola**:

```
OLLAMA_MODEL=qwen3.5:4b
CONTACT_EMAIL=seu.email@escola.edu.br
```

O e-mail é o contato exigido pelo Unpaywall (PDF aberto). Não é conta de aluno.

## 4. Rodar

Ollama precisa estar aberto. Depois:

```bat
cd C:\paperqa-gui-local
rodar-windows.bat
```

Ou:

```bat
cd C:\paperqa-gui-local
.venv\Scripts\activate
streamlit run app.py
```

Abra http://localhost:8501

## 5. O que testar (mesma tela do Linux)

Precisa de **internet** só na seção 2 (Oasisbr / Unpaywall). Ollama e a leitura do PDF são locais.

1. Faixa **verde** no topo: Ollama ok e `qwen3.5:4b` instalado.
2. **2. Buscar artigos** — tema `educação inclusiva` → Buscar. Deve aparecer Oasisbr (IBICT).
3. Se o botão **Baixar PDF aberto e indexar** estiver ativo, teste um. Se a SciELO devolver HTML/500, baixe o PDF no site e use **1. Enviar PDFs**.
4. Envie **um** PDF curto em **1. Enviar PDFs** e espere indexar.
5. **3. Pergunta** → Perguntar. A 1ª resposta pode levar alguns minutos. Não feche a aba.
6. Abra **Mostrar Fontes**.

Textos da tela: [FUNCOES.txt](FUNCOES.txt).

## Não faça

- Não instale `.venv` no pendrive
- Não use Docker neste PC da viagem (é extra; Python+Ollama já resolvem)
- Não comece a demo com o modelo 9B sem ter ensaiado
- Não rode com o `.env` do Linux (`PQA_HOME=/media/...`)
- Grave um vídeo de backup da tela funcionando
