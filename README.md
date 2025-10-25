# 🎙️ MILO Server

> **Modular Intelligent Listening Organizer**

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](docker/)

MILO es un servidor de asistente de voz modular e inteligente construido en Python que proporciona un pipeline completo de **Speech-to-Text (STT) → Large Language Model (LLM) → Text-to-Speech (TTS)** con clonación de voz. Diseñado para ser flexible, escalable y fácil de integrar mediante WebSockets.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
  - [Instalación Local](#instalación-local)
  - [Instalación con Docker](#instalación-con-docker)
- [Configuración](#-configuración)
- [Uso](#-uso)
  - [Modo Audio](#modo-audio)
  - [Modo Texto](#modo-texto)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API WebSocket](#-api-websocket)
- [Testing](#-testing)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## ✨ Características

- 🎤 **Speech-to-Text (STT)**: Transcripción de audio usando `faster-whisper` con soporte multiidioma
- 🧠 **Procesamiento LLM**: Múltiples proveedores disponibles:
  - **Ollama**: Agente local para privacidad total
  - **Gemini**: Agente remoto de Google AI para respuestas rápidas
- 🗣️ **Text-to-Speech (TTS)**: Múltiples backends disponibles:
  - **XTTS v2** (Coqui TTS): 
    - Modo PRESET: Voces predefinidas ultrarrápidas ⚡
    - Modo CLONE: Clonación de voz personalizada
  - **Piper TTS**: Rápido y ligero, ideal para CPU
- 🔌 **API WebSocket**: Comunicación en tiempo real para audio y texto
- 🐳 **Docker Ready**: Contenedores preconfigurados para GPU y CPU
- 🌍 **Multiidioma**: Soporte para español y otros idiomas
- 📊 **Respuestas Estructuradas**: Formato JSON con soporte para objetos especiales (código, tablas, etc.)
- ⚡ **Optimizado**: Uso eficiente de recursos con modelos cuantizados y caché inteligente

---

## 🏗️ Arquitectura

```text
┌─────────────┐
│   Cliente   │ (WebSocket)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      MILO Server (main.py)      │
│  ┌──────────────────────────┐   │
│  │   WebSocket Handler      │   │
│  └────────┬─────────────────┘   │
│           │                      │
│  ┌────────▼─────────┐            │
│  │  STT Processor   │ Whisper   │
│  └────────┬─────────┘            │
│           │                      │
│  ┌────────▼─────────┐            │
│  │  LLM Processor   │ Ollama    │
│  └────────┬─────────┘            │
│           │                      │
│  ┌────────▼─────────┐            │
│  │  TTS Processor   │ Coqui TTS │
│  └──────────────────┘            │
└─────────────────────────────────┘
```

### Componentes Principales

| Componente | Tecnología | Descripción |
|------------|-----------|-------------|
| **STT** | faster-whisper | Transcripción de audio a texto |
| **LLM** | Ollama (llama3) | Procesamiento de lenguaje natural |
| **TTS** | XTTS v2 / Piper | Síntesis de voz (preset o clone) |
| **API** | websockets | Comunicación bidireccional en tiempo real |

> 📖 **Documentación TTS**: 
> - [docs/PIPER_TTS.md](docs/PIPER_TTS.md) - Información sobre backend Piper
> - [docs/XTTS_MODES.md](docs/XTTS_MODES.md) - Modos PRESET vs CLONE de XTTS

---

## 📦 Requisitos Previos

### Software Requerido

- **Python 3.12+** ([Descargar](https://www.python.org/downloads/))
- **FFmpeg** (para procesamiento de audio)
- **CUDA 12.1+** (opcional, para aceleración GPU)
- **Proveedor LLM** (elige uno):
  - **Ollama** ([Instalar](https://ollama.ai/)) - Agente local
  - **Gemini API Key** ([Obtener](https://aistudio.google.com/app/apikey)) - Agente remoto

### Instalación de FFmpeg

**Ubuntu/Debian:**

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

**macOS (Homebrew):**

```bash
brew install ffmpeg
```

**Windows (Chocolatey):**

```bash
choco install ffmpeg
```

### Instalación de Ollama

Sigue las instrucciones en [ollama.ai](https://ollama.ai/) y descarga el modelo requerido:

```bash
ollama pull llama3:8b-instruct-q4_K_M
```

### Configuración de Gemini (Alternativa)

Si prefieres usar Gemini en lugar de Ollama:

1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Inicia sesión y crea una API key
3. Guarda la API key para la configuración

📖 **Ver más**: [docs/LLM_PROVIDERS.md](docs/LLM_PROVIDERS.md) para comparación detallada

---

## 🚀 Instalación

### Instalación Local

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/Briany4717/MILO-Server.git
   cd MILO-Server
   ```

2. **Crea y activa un entorno virtual:**

   ```bash
   python -m venv evenv
   source evenv/bin/activate  # En Windows: evenv\Scripts\activate
   ```

3. **Instala PyTorch con soporte CUDA (opcional):**

   ```bash
   pip install torch==2.4.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121
   ```

4. **Instala las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configura las variables de entorno:**

   ```bash
   cp .env.example .env
   # Edita .env con tus configuraciones
   ```

6. **Prepara el embedding de voz:**

   Coloca tu muestra de voz en `samples/` y ejecuta:

   ```bash
   python src/preload_voice.py
   ```

7. **Inicia el servidor:**

   ```bash
   python main.py
   ```

   El servidor estará disponible en `ws://0.0.0.0:8765`

### Instalación con Docker

#### Opción 1: Docker Compose (Recomendado)

```bash
cd docker/
docker-compose up --build
```

Esto iniciará:
- **MILO Server** en el puerto `8765`
- **Ollama** en el puerto `11434`

#### Opción 2: Build Manual

**Para GPU:**

```bash
cd docker/
docker build -f Dockerfile.gpu -t milo-server:gpu ..
docker run --rm -it --gpus all -p 8765:8765 --env-file ../.env milo-server:gpu
```

**Para CPU:**

```bash
cd docker/
docker build -f Dockerfile.optimized.final -t milo-server:cpu ..
docker run --rm -it -p 8765:8765 --env-file ../.env milo-server:cpu
```

> **Nota:** Para usar GPU, necesitas [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

---

## ⚙️ Configuración

Crea un archivo `.env` en la raíz del proyecto (o copia `.env.example`):

```env
# Configuración de Red
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8765

# Modelo Whisper: tiny, base, small, medium, large
WHISPER_MODEL_SIZE=base

# Proveedor LLM: "ollama" (local) o "gemini" (remoto)
LLM_PROVIDER=ollama

# Configuración Ollama (si LLM_PROVIDER=ollama)
OLLAMA_MODEL=llama3:8b-instruct-q4_K_M
OLLAMA_BASE_URL=http://localhost:11434/v1

# Configuración Gemini (si LLM_PROVIDER=gemini)
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-1.5-flash

# Backend TTS: "xtts" (clonación de voz) o "piper" (rápido y ligero)
TTS_BACKEND=xtts

# Configuración XTTS v2 (solo si TTS_BACKEND=xtts)
TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
TTS_SPEAKER_WAV=samples/alejandro_sample_v2.wav

# Configuración Piper TTS (solo si TTS_BACKEND=piper)
PIPER_MODEL_PATH=models/piper/es_ES-sharvard-medium.onnx
PIPER_CONFIG_PATH=models/piper/es_ES-sharvard-medium.onnx.json
PIPER_SPEAKER_ID=0
```

### Variables Importantes

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `WEBSOCKET_HOST` | Host del servidor WebSocket | `0.0.0.0` |
| `WEBSOCKET_PORT` | Puerto del servidor | `8765` |
| `WHISPER_MODEL_SIZE` | Tamaño del modelo Whisper | `base` |
| `LLM_PROVIDER` | Proveedor LLM: `ollama` o `gemini` | `ollama` |
| `OLLAMA_MODEL` | Modelo de Ollama (si es local) | `llama3:8b-instruct-q4_K_M` |
| `GEMINI_API_KEY` | API Key de Gemini (si es remoto) | - |
| `GEMINI_MODEL` | Modelo de Gemini | `gemini-1.5-flash` |
| `TTS_BACKEND` | Backend TTS: `xtts` o `piper` | `xtts` |
| `TTS_MODEL` | Modelo de Coqui TTS (XTTS) | `xtts_v2` |
| `TTS_SPEAKER_WAV` | Audio para clonar voz (XTTS) | `samples/alejandro_sample_v2.wav` |
| `PIPER_MODEL_PATH` | Ruta al modelo Piper | `models/piper/es_ES-sharvard-medium.onnx` |

> 💡 **Tip**: Para usar Piper TTS, ejecuta `./scripts/download_piper_model.sh` para descargar un modelo español.
> Ver [docs/PIPER_TTS.md](docs/PIPER_TTS.md) para más información sobre backends TTS.

---

## 🎯 Uso

### Modo Audio

El cliente envía audio en formato WAV y recibe la respuesta sintetizada en audio.

**Protocolo:**

1. Cliente se conecta al WebSocket
2. Cliente envía: `"modo audio"`
3. Cliente envía frames de audio (bytes)
4. Cliente envía: `"Fin de Audio"`
5. Servidor procesa y responde con audio sintetizado

**Ejemplo en Python:**

```python
import asyncio
import websockets
import wave

async def send_audio():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Activar modo audio
        await websocket.send("modo audio")
        
        # Enviar archivo de audio
        with open("audio.wav", "rb") as f:
            audio_data = f.read()
            await websocket.send(audio_data)
        
        # Señal de fin
        await websocket.send("Fin de Audio")
        
        # Recibir respuesta
        await websocket.recv()  # "Inicio de Respuesta"
        
        audio_chunks = []
        while True:
            chunk = await websocket.recv()
            if isinstance(chunk, str) and chunk == "Fin de Respuesta":
                break
            audio_chunks.append(chunk)
        
        # Guardar audio recibido
        with open("response.wav", "wb") as f:
            f.write(b"".join(audio_chunks))

asyncio.run(send_audio())
```

### Modo Texto

El cliente envía texto plano y recibe la respuesta sintetizada en audio.

**Protocolo:**

1. Cliente se conecta al WebSocket
2. Cliente envía: `"modo texto"`
3. Cliente envía el mensaje de texto
4. Servidor procesa y responde con audio sintetizado

**Ejemplo en Python:**

```python
import asyncio
import websockets

async def send_text():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Activar modo texto
        await websocket.send("modo texto")
        
        # Enviar mensaje
        await websocket.send("¿Cuál es la capital de Francia?")
        
        # Recibir respuesta
        await websocket.recv()  # "Inicio de Respuesta"
        
        audio_chunks = []
        while True:
            chunk = await websocket.recv()
            if isinstance(chunk, str) and chunk == "Fin de Respuesta":
                break
            audio_chunks.append(chunk)
        
        # Guardar audio
        with open("response.wav", "wb") as f:
            f.write(b"".join(audio_chunks))

asyncio.run(send_text())
```

---

## 📁 Estructura del Proyecto

```text
MILO-Server/
├── 📄 main.py                    # Punto de entrada del servidor
├── 📄 requirements.txt            # Dependencias de Python
├── 📄 .env.example                # Plantilla de configuración
├── 📄 .gitignore                  # Archivos ignorados por Git
├── 📄 README.md                   # Este archivo
├── 📄 LICENSE                     # Licencia del proyecto
├── 📄 CHANGELOG.md                # Historial de cambios
├── 📄 CODE_OF_CONDUCT.md          # Código de conducta
├── 📄 CONTRIBUTING.md             # Guía de contribución
│
├── 📁 src/                        # Código fuente
│   ├── 📄 config.py               # Configuración global
│   ├── 📄 stt_processor.py        # Procesador STT (Whisper)
│   ├── 📄 llm_processor.py        # Procesador LLM (Ollama)
│   ├── 📄 tts_processor.py        # Procesador TTS (Coqui)
│   └── 📄 preload_voice.py        # Script para preparar voz
│
├── 📁 scripts/                    # Scripts auxiliares
│   ├── 📄 preload_tts.py          # Pre-carga de modelos TTS
│   ├── 📄 cleanup.sh              # Limpieza de archivos temporales
│   └── 📄 smart-build.sh          # Build inteligente de Docker
│
├── 📁 docker/                     # Configuración Docker
│   ├── 📄 Dockerfile.gpu          # Imagen para GPU
│   ├── 📄 Dockerfile.optimized.final  # Imagen para CPU
│   ├── 📄 docker-compose.yml      # Orquestación de servicios
│   └── 📄 docker-compose.dev.yml  # Configuración de desarrollo
│
├── 📁 tests/                      # Tests automatizados
│   └── 📄 e2e_test.py             # Test end-to-end
│
├── 📁 data/                       # Datos y modelos
│   ├── 📄 voice_embedding.pth     # Embedding de voz pre-calculado
│   └── 📁 ollama-models/          # Modelos de Ollama (ignorado)
│
├── 📁 samples/                    # Muestras de audio
│   └── 📄 alejandro_sample_v2.wav # Muestra de voz de ejemplo
│
├── 📁 docs/                       # Documentación adicional
│   └── 📄 DOCKERFILES.md          # Documentación de Dockerfiles
│
└── 📁 ci/                         # Integración continua
    └── 📄 smoke_check.py          # Prueba de humo
```

---

## 🔌 API WebSocket

### Endpoint

```text
ws://<host>:<port>
```

Por defecto: `ws://0.0.0.0:8765`

### Protocolo de Comunicación

#### Modo Audio

**Cliente → Servidor:**

1. `"modo audio"` (string)
2. `<audio_bytes>` (bytes, múltiples frames)
3. `"Fin de Audio"` (string)

**Servidor → Cliente:**

1. `"Inicio de Respuesta"` (string)
2. `<audio_bytes>` (bytes, múltiples chunks)
3. `"Fin de Respuesta"` (string)

#### Modo Texto

**Cliente → Servidor:**

1. `"modo texto"` (string)
2. `<mensaje_texto>` (string)

**Servidor → Cliente:**

1. `"Inicio de Respuesta"` (string)
2. `<audio_bytes>` (bytes, múltiples chunks)
3. `"Fin de Respuesta"` (string)

### Formato de Respuesta del LLM

El LLM responde en formato JSON estructurado:

```json
{
  "mensaje": "La respuesta principal que será convertida a voz",
  "objetos": [
    {
      "tipo": "codigo",
      "contenido": "print('Hola mundo')"
    },
    {
      "tipo": "tabla",
      "contenido": "| Col1 | Col2 |\n|------|------|\n| A    | B    |"
    }
  ]
}
```

**Campos:**

- `mensaje` (obligatorio): Texto que se sintetizará en voz
- `objetos` (opcional): Lista de objetos estructurados (código, tablas, etc.)

---

## 🧪 Testing

### Test End-to-End

Ejecuta el test completo del pipeline:

```bash
python tests/e2e_test.py
```

Este test:
1. Transcribe un archivo de audio de muestra
2. Envía el texto al LLM
3. Genera audio con la respuesta
4. Guarda el resultado en `response_e2e.wav`

### Test en Docker

```bash
docker-compose exec milo-server python tests/e2e_test.py
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor, lee [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles sobre nuestro proceso de desarrollo.

### Pasos para Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Código de Conducta

Este proyecto sigue el [Código de Conducta](CODE_OF_CONDUCT.md). Al participar, se espera que lo respetes.

---

## 📝 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- [Coqui TTS](https://github.com/coqui-ai/TTS) - Motor de síntesis de voz
- [OpenAI Whisper](https://github.com/openai/whisper) - Modelo de transcripción
- [Ollama](https://ollama.ai/) - Framework para LLMs locales
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Implementación optimizada de Whisper

---

## 📧 Contacto

**Briany4717** - [@Briany4717](https://github.com/Briany4717)

**Link del Proyecto:** [https://github.com/Briany4717/MILO-Server](https://github.com/Briany4717/MILO-Server)

---

<div align="center">
  <p>Hecho con ❤️ por Briany4717</p>
  <p>⭐ Si te gusta este proyecto, por favor dale una estrella ⭐</p>
</div>
