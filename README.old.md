# 🎙️ MILO Server

**Modular Intelligent Listening Organizer**

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](docker/)

MILO es un servidor de asistente de voz modular e inteligente construido en Python que proporciona un pipeline completo de Speech-to-Text (STT) → Large Language Model (LLM) → Text-to-Speech (TTS) con clonación de voz. Diseñado para ser flexible, escalable y fácil de integrar mediante WebSockets.

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
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API WebSocket](#-api-websocket)
- [Testing](#-testing)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## ✨ Características

- **🎤 Speech-to-Text (STT)**: Transcripción de audio usando `faster-whisper` con soporte multiidioma
- **🧠 Procesamiento LLM**: Integración con Ollama para respuestas inteligentes y contextuales
- **🗣️ Text-to-Speech (TTS)**: Síntesis de voz con clonación usando Coqui TTS (XTTS v2)
- **🔌 API WebSocket**: Comunicación en tiempo real para audio y texto
- **🐳 Docker Ready**: Contenedores preconfigurados para GPU y CPU
- **🌍 Multiidioma**: Soporte para español y otros idiomas
- **📊 Respuestas Estructuradas**: Formato JSON con soporte para objetos especiales (código, tablas, etc.)
- **⚡ Optimizado**: Uso eficiente de recursos con modelos cuantizados y caché inteligente

---

## 🏗️ Arquitectura

```
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
| **TTS** | Coqui TTS (XTTS v2) | Síntesis de voz con clonación |
| **API** | websockets | Comunicación bidireccional en tiempo real |

---

## 📦 Requisitos Previos

### Software Requerido

- **Python 3.12+** ([Descargar](https://www.python.org/downloads/))
- **Ollama** ([Instalar](https://ollama.ai/))
- **FFmpeg** (para procesamiento de audio)
- **CUDA 12.1+** (opcional, para aceleración GPU)

### Instalación de FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg

    ```bash```bash

    cp .env.example .env

    ```brew install ffmpeg```bash



2.  **Descarga el modelo de Ollama:**```brew install ffmpeg

    Asegúrate de que el modelo especificado en tu `.env` (p. ej., `llama3:8b-instruct-q4_K_M`) esté disponible localmente.

    ```bash```

    ollama pull llama3:8b-instruct-q4_K_M

    ```## Instalación rápida



## Ejecución## Instalación rápida



Para iniciar el servidor:1.  Clona el repositorio:

```bash

python main.py1. Clona el repositorio:

```

El servicio estará disponible en `ws://0.0.0.0:8765` por defecto.    ```bash



## Uso con Docker    git clone <URL-del-repositorio>```bash



### Construcción de Imágenes    cd MILO-Servergit clone <URL-del-repositorio>



-   **CPU:**    ```cd MILO-Server

    ```bash

    docker build -f Dockerfile.optimized.final -t milo-server:cpu .```

    ```

-   **GPU:**2.  Crea y activa un entorno virtual:

    ```bash

    docker build -f Dockerfile.gpu -t milo-server:gpu .1. Crea y activa un entorno virtual:

    ```

    ```bash

### Ejecución de Contenedores

    python -m venv evenv```bash

-   **Con `docker-compose` (Recomendado):**

    Inicia todos los servicios (incluido Ollama) con un solo comando.    source evenv/bin/activatepython -m venv evenv

    ```bash

    docker-compose up --build    ```source evenv/bin/activate

    ```

```

-   **Manualmente (Contenedor GPU):**

    ```bash3.  Instala dependencias:

    docker run --rm -it --gpus all --network="host" --env-file .env milo-server:gpu

    ```1. Instala dependencias:

    *Nota: Para usar la GPU, necesitas los **controladores NVIDIA** y el **NVIDIA Container Toolkit** en tu sistema host.*

    ```bash

### Pre-carga de Modelos TTS en el Build

    pip install -r requirements.txt```bash

Para evitar descargas en el primer arranque, puedes pre-cargar los modelos de Coqui TTS durante la construcción de la imagen usando el script `smart-build.sh`.

    ```pip install -r requirements.txt

```bash

./smart-build.sh gpu preload-tts```

```

## Configuración

> **Advertencia sobre Licencias**: Este proceso puede aceptar automáticamente los términos de licencia de los modelos (p. ej., CPML). Es tu responsabilidad revisar y cumplir con dichas licencias antes de distribuir cualquier imagen.

## Configuración

## Pruebas

1.  Copia el archivo de ejemplo `.env.example` y edita las variables necesarias:

### Prueba End-to-End (E2E)

1. Copia el ejemplo y edita las variables necesarias:

Este test ejecuta el pipeline completo (STT → LLM → TTS) y genera un archivo `response_e2e.wav`.

    ```bash

-   **Dentro del contenedor (Recomendado):**

    ```bash    cp .env.example .env```bash

    docker exec -it milo-server python e2e_test.py

    ```    ```cp .env.example .env

-   **Localmente:**

    ```bash```

    python e2e_test.py

    ```2.  Ejemplo de variables en `.env`:



### Smoke Test (CI)1. Variables de ejemplo en `.env`:



El script `ci/smoke_check.py` está diseñado para flujos de CI. Verifica imports críticos y la disponibilidad de PyTorch sin requerir una GPU.    ```ini



```bash    WEBSOCKET_HOST="0.0.0.0"```ini

python ci/smoke_check.py

```    WEBSOCKET_PORT=8765WEBSOCKET_HOST="0.0.0.0"



## Contribuciones    WHISPER_MODEL_SIZE="base"WEBSOCKET_PORT=8765



Las contribuciones son bienvenidas. Por favor, lee `CONTRIBUTING.md` para más detalles y abre un *issue* para discutir cambios importantes.    OLLAMA_MODEL="llama3:8b-instruct-q4_K_M"WHISPER_MODEL_SIZE="base"



## Licencia    TTS_MODEL="tts_models/multilingual/multi-dataset/xtts_v2"OLLAMA_MODEL="llama3:8b-instruct-q4_K_M"



Este proyecto está distribuido bajo los términos de la licencia especificada en el archivo `LICENSE`.    TTS_SPEAKER_WAV="samples/alejandro_sample_v2.wav"TTS_MODEL="tts_models/multilingual/multi-dataset/xtts_v2"


    ```TTS_SPEAKER_WAV="samples/alejandro_sample_v2.wav"

```

3.  Si usas Ollama localmente, descarga el modelo necesario:

1. Si usas Ollama localmente, descarga el modelo necesario:

    ```bash

    ollama pull llama3:8b-instruct-q4_K_M```bash

    ```ollama pull llama3:8b-instruct-q4_K_M

```

## Ejecutar el servidor

## Ejecutar el servidor

```bash

python main.py```bash

```python main.py

```

Por defecto, el servicio escucha en `ws://0.0.0.0:8765`.

Por defecto el servicio escucha en `ws://0.0.0.0:8765`.

## Docker (CPU y GPU)

## Docker (CPU y GPU)

### Build

1. Build (CPU):

- **CPU**:

  ```bash```bash

  docker build -f Dockerfile.optimized.final -t milo-server:cpu .docker build -f Dockerfile.optimized.final -t milo-server:optimized .

  ``````

- **GPU**:

  ```bash1. Build (GPU):

  docker build -f Dockerfile.gpu -t milo-server:gpu .

  ``````bash

docker build -f Dockerfile.gpu -t milo-server:gpu .

### Run (GPU)```



```bash1. Run (GPU):

docker run --rm -it --gpus all --network="host" --env-file .env milo-server:gpu

``````bash

docker run --rm -it --gpus all --network="host" --env-file .env milo-server:gpu

**Notas**:```



- Asegúrate de tener los **controladores NVIDIA** y **NVIDIA Container Toolkit** instalados en el host.Notas:

- Para evitar `sudo` al ejecutar Docker, añade tu usuario al grupo `docker`: `sudo usermod -aG docker $USER`.

1. Asegúrate de tener los controladores NVIDIA y NVIDIA Container Toolkit instalados en el host.

## Pre-carga de modelos TTS (Build)1. Para evitar `sudo` al ejecutar Docker, añade tu usuario al grupo `docker`:



Para evitar descargas y prompts de licencia al primer arranque, puedes pre-cargar los modelos de Coqui TTS durante la etapa de build.```bash

sudo usermod -aG docker $USER

Usa el script `smart-build.sh` para facilitar el proceso:```



```bash## Prueba E2E

./smart-build.sh gpu preload-tts

```Prueba completa (STT → LLM → TTS) que genera `response_e2e.wav`.



**Advertencia sobre licencias**: Algunos modelos (p. ej., con licencia CPML) requieren aceptación explícita. El pre-cargador automatiza este paso. **Revisa la licencia del modelo antes de distribuir imágenes públicas.**1. Desde el contenedor (recomendado):



## Pruebas```bash

docker run --rm --gpus all --network="host" --env-file .env -v $(pwd):/workspace -w /workspace milo-server:gpu python -u e2e_test.py

### Prueba E2E```



Este test ejecuta el pipeline completo (STT → LLM → TTS) y genera un archivo `response_e2e.wav`.1. O localmente en tu venv:



- **Desde el contenedor (recomendado)**:```bash

  ```bashpython e2e_test.py

  docker run --rm --gpus all --network="host" --env-file .env -v $(pwd):/workspace -w /workspace milo-server:gpu python -u e2e_test.py```

  ```

- **Localmente**:Si aparece OOM en CUDA, el script sintetiza por frases y concatena WAVs parciales para reducir picos de memoria.

  ```bash

  python e2e_test.py## Pre-carga de modelos TTS durante el build

  ```

Si quieres evitar descargas y prompts al primer arranque, puedes pre-cargar modelos TTS durante la etapa de build y copiar la caché al usuario runtime.

### Smoke Test (CI)

1. Ejemplo (usa `smart-build.sh`):

El script `ci/smoke_check.py` verifica imports críticos y la disponibilidad de PyTorch. Es ideal para flujos de CI sin GPU.

```bash

```bash./smart-build.sh gpu preload-tts

python ci/smoke_check.py```

```

Qué hace:

## Contribuir

1. Descarga el modelo TTS en una etapa temporal del build.

Lee `CONTRIBUTING.md` antes de enviar Pull Requests. Para cambios mayores, por favor, abre un *issue* primero para discutirlo.1. Copia la caché de `/root/.local/share/tts` a `/home/appuser/.local/share/tts` y ajusta permisos.



## LicenciaAdvertencia sobre licencias:



Este proyecto está bajo la licencia especificada en el archivo `LICENSE`.Algunos modelos (por ejemplo con licencia CPML) requieren aceptación explícita. El preloader puede automatizar la aceptación durante el build, pero revisa la licencia antes de distribuir imágenes públicas.


## Caché y volúmenes recomendados

Usa volúmenes para caches de modelos y datos:

- `model-cache` (modelos TTS/LLM)
- `torch-cache` (caché PyTorch)
- `transformers-cache` (Hugging Face)

El `docker-compose.yml` incluye un ejemplo de volúmenes.

## Smoke test local

Script: `ci/smoke_check.py`.

```bash
# activa tu venv si procede
python -m pip install -r requirements.txt
python ci/smoke_check.py
```

El script verifica imports críticos y hace una comprobación rápida de PyTorch en CPU; ideal para CI sin GPU.

## Contribuir

Lee `CONTRIBUTING.md` antes de abrir PRs. Para cambios grandes, abre primero un issue.

## Licencia

Revisa `LICENSE` en la raíz del repositorio para los términos del proyecto.



```

El script verifica imports críticos y hace una comprobación rápida de PyTorch en CPU.

## Contribuir

Lee `CONTRIBUTING.md` antes de abrir PRs. Para cambios mayores, abre primero un *issue*.

## Licencia

Consulta `LICENSE` en la raíz del proyecto para los términos del proyecto.

## Licencia

Consulta `LICENSE` en la raíz del proyecto para los términos del proyecto.

El archivo `docker-compose.yml` en este repositorio contiene un ejemplo de volúmenes y servicios.

## Ejecutar el smoke test localmente

Script: `ci/smoke_check.py`.

```bash
# activa tu venv si procede
python -m pip install -r requirements.txt
python ci/smoke_check.py
```

El script verifica imports críticos y hace una comprobación rápida de PyTorch en CPU.

## Contribuir

Las contribuciones son bienvenidas. Para cambios mayores, abre un *issue* primero y sigue `CONTRIBUTING.md`.

## Licencia

Revisa `LICENSE` en la raíz del repositorio para los términos del proyecto.

# O localmente en tu venv:
python e2e_test.py
```

Si aparece OOM en CUDA, el script sintetiza por frases y concatena WAVs parciales para reducir picos de memoria.

### Pre-carga de modelos TTS durante el build (preload-tts)

Para evitar que Coqui TTS descargue modelos al primer arranque, es posible pre-descargarlos en la etapa de build y copiar la caché al usuario runtime.

Ejemplo (usa `smart-build.sh`):

```bash
./smart-build.sh gpu preload-tts
```

Qué hace:

- Fuerza la descarga del modelo en una etapa temporal del build.
- Copia la caché de `/root/.local/share/tts` a `/home/appuser/.local/share/tts` y ajusta permisos.

Notas sobre licencia (CPML):

- Algunos modelos requieren aceptación de licencia (p. ej. CPML). El preloader puede automatizar esta aceptación en el build. Revisa la licencia del modelo antes de distribuir la imagen.

Cache y volúmenes recomendados:

# MILO: Asistente de Voz Modular

MILO (Modular Intelligent Listening Organizer) es un servidor de asistente de voz basado en Python. Usa una arquitectura modular para STT (reconocimiento), LLM (razonamiento) y TTS (síntesis) y expone una API por WebSockets.

## Tecnología y arquitectura

- STT: faster-whisper
- LLM: Ollama (cliente local)
# MILO: Asistente de Voz Modular

MILO (Modular Intelligent Listening Organizer) es un servidor de asistente de voz modular escrito en Python. Combina reconocimiento de voz (STT), modelos de lenguaje (LLM) y síntesis de voz (TTS). Expone una API por WebSockets para recibir audio, procesarlo y devolver una respuesta hablada.

## Resumen rápido
# MILO: Asistente de Voz Modular

MILO (Modular Intelligent Listening Organizer) es un servidor de asistente de voz modular escrito en Python. Combina reconocimiento de voz (STT), modelos de lenguaje (LLM) y síntesis de voz (TTS). Expone una API por WebSockets para recibir audio, procesarlo y devolver una respuesta hablada.

## Resumen rápido
# MILO: Asistente de Voz Modular

MILO (Modular Intelligent Listening Organizer) es un servidor de asistente de voz modular escrito en Python. Combina reconocimiento de voz (STT), modelos de lenguaje (LLM) y síntesis de voz (TTS). Expone una API por WebSockets para recibir audio, procesarlo y devolver una respuesta hablada.

## Resumen rápido

- STT: `faster-whisper`
- LLM: `Ollama` (cliente local)
- TTS: `Coqui TTS`
- API: `Flask` + WebSockets

## Requisitos

- Python 3.10 o superior
- Ollama (instalación local — ver la documentación oficial)
- `ffmpeg`

Instalar `ffmpeg` (Debian/Ubuntu):

```bash
sudo apt-get install ffmpeg
```

macOS (Homebrew):

```bash
brew install ffmpeg
```

## Instalación

1. Clona el repositorio:

```bash
git clone <URL-del-repositorio>
cd MILO-Server
```

1. Crea y activa un entorno virtual:

```bash
python -m venv evenv
source evenv/bin/activate
```

1. Instala dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

Copia el ejemplo y edita lo necesario:

```bash
cp .env.example .env
```

Variables de ejemplo (en `.env`):

```ini
WEBSOCKET_HOST="0.0.0.0"
WEBSOCKET_PORT=8765
WHISPER_MODEL_SIZE="base"
OLLAMA_MODEL="llama3:8b-instruct-q4_K_M"
TTS_MODEL="tts_models/multilingual/multi-dataset/xtts_v2"
TTS_SPEAKER_WAV="samples/alejandro_sample_v2.wav"
```

Si usas Ollama localmente, descarga el modelo:

```bash
ollama pull llama3:8b-instruct-q4_K_M
```

## Ejecutar

Inicia el servidor:

```bash
python main.py
```

Por defecto: `ws://0.0.0.0:8765`.

## Docker (CPU y GPU)

Build (CPU):

```bash
docker build -f Dockerfile.optimized.final -t milo-server:optimized .
```

Build (GPU):

```bash
docker build -f Dockerfile.gpu -t milo-server:gpu .
```

Run (GPU):

```bash
docker run --rm -it --gpus all --network="host" --env-file .env milo-server:gpu
```

Notas:

- Asegúrate de tener los controladores NVIDIA y NVIDIA Container Toolkit instalados en el host.
- Para evitar `sudo` al ejecutar docker, añade tu usuario al grupo `docker`:

```bash
sudo usermod -aG docker $USER
```

## Prueba E2E

Ejecuta la prueba end-to-end (STT -> LLM -> TTS). Desde el contenedor (recomendado):

```bash
docker run --rm --gpus all --network="host" --env-file .env -v $(pwd):/workspace -w /workspace milo-server:gpu python -u e2e_test.py
```

O localmente en tu entorno virtual:

```bash
python e2e_test.py
```

Si aparece OOM en CUDA, el script sintetiza por frases y concatena WAVs parciales para reducir picos de memoria.

## Pre-carga de modelos TTS durante el build (preload-tts)

Para evitar descargas al primer arranque, el repositorio incluye un flujo para pre-cargar el modelo TTS durante la etapa de build y copiar la caché al usuario runtime.

Ejemplo (usa `smart-build.sh`):

```bash
./smart-build.sh gpu preload-tts
```

Qué hace:

1. Descarga el modelo en una etapa temporal del build.
2. Copia la caché de `/root/.local/share/tts` a `/home/appuser/.local/share/tts` y ajusta permisos.

Advertencia sobre licencias:

Algunos modelos llevan licencias que requieren aceptación explícita (por ejemplo CPML). El preloader puede automatizar la aceptación durante el build para CI, pero revisa la licencia antes de distribuir imágenes públicas.

## Caché y volúmenes recomendados

Usa volúmenes para evitar re-descargas:

- `model-cache` (modelos TTS/LLM)
- `torch-cache` (caché PyTorch)
- `transformers-cache` (huggingface)

El `docker-compose.yml` incluye ejemplos de volúmenes y servicios.

## Smoke test local

Script: `ci/smoke_check.py`.

```bash
# activa tu venv si procede
python -m pip install -r requirements.txt
python ci/smoke_check.py
```

El script verifica imports críticos y hace una comprobación rápida de PyTorch en CPU.

## Contribuir

Lee `CONTRIBUTING.md` antes de abrir PRs. Para cambios mayores, abre primero un *issue*.

## Licencia

Consulta `LICENSE` en la raíz del proyecto.

```

El script verifica imports críticos y hace una comprobación rápida de PyTorch en CPU.

## Contribuir

Lee `CONTRIBUTING.md` antes de abrir PRs. Para cambios mayores, abre primero un *issue*.

## Licencia

Consulta `LICENSE` en la raíz del proyecto.

```

El script verifica imports críticos y hace una comprobación rápida de PyTorch en CPU.

## Contribuir

Lee `CONTRIBUTING.md` antes de abrir PRs. Para cambios mayores, abre primero un *issue*.

## Licencia

Consulta `LICENSE` en la raíz del proyecto.

Si quieres evitar que Coqui TTS descargue modelos la primera vez que arranca el contenedor, puedes pre-descargarlos durante la etapa de build y copiar la caché resultante al usuario de runtime. Esto reduce tiempo de arranque y evita prompts interactivos durante la primera ejecución.

Usando el script `smart-build.sh` puedes activar la opción `preload-tts` (requiere conexión a Internet durante el build):

```bash
./smart-build.sh gpu preload-tts
```

Qué hace esto:
- Instancia Coqui TTS en una etapa temporal del build y fuerza la descarga del modelo configurado en `TTS_MODEL`.
- Copia la caché de TTS desde el usuario root de build (`/root/.local/share/tts`) a la ruta del usuario runtime (`/home/appuser/.local/share/tts`) y ajusta permisos.

Notas sobre licencia (CPML):
- Algunos modelos de TTS (p. ej. modelos de Coqui con licencia CPML) requieren aceptar una licencia al descargarse por primera vez. El preloader automatiza esto durante el build para evitar prompts interactivos, pero asegúrate de que tu uso cumple la licencia del modelo. Si tienes dudas legales, consulta la licencia del modelo antes de distribuir la imagen.

Cache y volúmenes recomendados
- En `docker-compose.yml` usamos volúmenes dedicados para caches (p. ej. `model-cache`, `torch-cache`, `transformers-cache`) para evitar re-descargas y ahorrar ancho de banda.

Si prefieres no pre-cargar durante el build, el contenedor descargará los modelos la primera vez que se instancien en runtime — este comportamiento es por defecto.

### Ejecutar el smoke test localmente

El proyecto incluye un script ligero para CI/validación rápida ubicado en `ci/smoke_check.py`. Para ejecutar localmente en tu entorno (sin GPU) haz:

```bash
# activa tu venv si lo usas
python -m pip install -r requirements.txt
python ci/smoke_check.py
```

El script verifica imports críticos y hace una comprobación rápida de PyTorch en CPU. Está pensado para ejecutarse en runners de CI que no disponen de GPU.

