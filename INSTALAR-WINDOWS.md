# Instalar no Windows 11 (i7 + SSD) a partir do pendrive

Este é o caminho certo para o PC da apresentação: **Python + Ollama nativos no SSD**.  
Não rode o projeto de dentro do pendrive (ele está em exFAT; o `.venv` quebra).

## 0. Copiar para o SSD

No Explorer: copie a pasta `paperqa-gui-local` do pendrive para, por exemplo:

`C:\paperqa-gui-local`

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

Ou, à mão:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -c constraints-cpu.txt --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
copy .env.example .env
```

Edite o `.env` e deixe:

```
OLLAMA_MODEL=qwen3.5:4b
```

(O `.env.example` ainda traz 9b; na apresentação comece no 4b.)

## 4. Rodar

Ollama precisa estar aberto. Depois:

```bat
cd C:\paperqa-gui-local
.venv\Scripts\activate
streamlit run app.py
```

Abra http://localhost:8501  
Faça upload de **um** PDF curto e pergunte. A 1ª resposta pode levar alguns minutos (carga do modelo).

## Não faça

- Não instale `.venv` no pendrive
- Não use Docker neste PC da viagem (é extra; Python+Ollama já resolvem)
- Não comece a demo com o modelo 9B sem ter ensaiado
- Grave um vídeo de backup da tela funcionando
