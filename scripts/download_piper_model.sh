#!/bin/bash
# Script para descargar modelos de Piper TTS desde Hugging Face
# Uso: ./scripts/download_piper_model.sh [modelo]
# Ejemplo: ./scripts/download_piper_model.sh es_ES-sharvard-medium

set -e

MODELS_DIR="models/piper"
BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/es"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_info() {
    echo -e "${BLUE}${NC} $1"
}

print_success() {
    echo -e "${GREEN}${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}${NC} $1"
}

print_error() {
    echo -e "${RED}${NC} $1"
}

# Modelos disponibles en español
declare -A MODELS=(
    ["es_ES-sharvard-medium"]="sharvard/medium - 56 MB - Calidad media, buena velocidad (RECOMENDADO)"
    ["es_ES-davefx-medium"]="davefx/medium - 58 MB - Calidad media"
    ["es_ES-carlfm-x_low"]="carlfm/x_low - 18 MB - Muy rápido, calidad básica"
    ["es_MX-ald-medium"]="ald/medium - 63.4 MB - Calidad media, voz masculina mexicana"
    ["es_MX-claude-high"]="claude/high - 63.3 MB - Alta calidad, voz masculina mexicana"
)

# Mapeo de nombres amigables a rutas en HuggingFace
declare -A MODEL_PATHS=(
    ["es_ES-sharvard-medium"]="es_ES/sharvard/medium"
    ["es_ES-davefx-medium"]="es_ES/davefx/medium"
    ["es_ES-carlfm-x_low"]="es_ES/carlfm/x_low"
    ["es_MX-ald-medium"]="es_MX/ald/medium"
    ["es_MX-claude-high"]="es_MX/claude/high"
)

# Función para mostrar modelos disponibles
show_models() {
    echo ""
    print_info "Modelos de Piper TTS disponibles en español:"
    echo ""
    for model in "${!MODELS[@]}"; do
        echo "  • ${model}"
        echo "    ${MODELS[$model]}"
        echo ""
    done
}

# Función para descargar un modelo
download_model() {
    local MODEL_NAME=$1
    
    if [ -z "$MODEL_NAME" ]; then
        print_error "Debes especificar un nombre de modelo"
        show_models
        exit 1
    fi
    
    # Verificar si el modelo existe en la lista
    if [ -z "${MODELS[$MODEL_NAME]}" ]; then
        print_error "Modelo no reconocido: $MODEL_NAME"
        show_models
        exit 1
    fi
    
    print_info "Descargando modelo: $MODEL_NAME"
    print_info "Descripción: ${MODELS[$MODEL_NAME]}"
    
    # Crear directorio si no existe
    mkdir -p "$MODELS_DIR"
    
    # Obtener la ruta del modelo en HuggingFace
    MODEL_PATH="${MODEL_PATHS[$MODEL_NAME]}"
    
    # URLs de descarga desde Hugging Face
    ONNX_URL="${BASE_URL}/${MODEL_PATH}/${MODEL_NAME}.onnx"
    JSON_URL="${BASE_URL}/${MODEL_PATH}/${MODEL_NAME}.onnx.json"

    # Nombre de archivo local
    LOCAL_ONNX="${MODELS_DIR}/${MODEL_NAME}.onnx"
    LOCAL_JSON="${MODELS_DIR}/${MODEL_NAME}.onnx.json"
    
    print_info "Descargando desde Hugging Face..."
    echo "URL: $ONNX_URL"
    
    # Descargar archivo .onnx usando curl con mejor manejo de redirecciones
    print_info "Descargando es_ES-${MODEL_NAME}.onnx..."
    if curl -L --fail --progress-bar -o "$LOCAL_ONNX" "$ONNX_URL"; then
        print_success "Archivo .onnx descargado ($(du -h "$LOCAL_ONNX" | cut -f1))"
    else
        print_error "Error al descargar el archivo .onnx"
        print_error "URL: $ONNX_URL"
        rm -f "$LOCAL_ONNX"
        exit 1
    fi
    
    # Descargar archivo .json
    print_info "Descargando es_ES-${MODEL_NAME}.onnx.json..."
    if curl -L --fail --progress-bar -o "$LOCAL_JSON" "$JSON_URL"; then
        print_success "Archivo .json descargado"
    else
        print_error "Error al descargar el archivo .json"
        print_error "URL: $JSON_URL"
        rm -f "$LOCAL_JSON"
        exit 1
    fi
    
    print_success "Modelo descargado correctamente en: ${MODELS_DIR}"
    echo ""
    print_info "Para usar este modelo, actualiza tu archivo .env:"
    echo ""
    echo "  TTS_BACKEND=piper"
    echo "  PIPER_MODEL_PATH=${MODELS_DIR}/${MODEL_NAME}.onnx"
    echo "  PIPER_CONFIG_PATH=${MODELS_DIR}/${MODEL_NAME}.onnx.json"
    echo "  PIPER_SPEAKER_ID=0"
    echo ""
    print_info "Puedes probar el modelo con:"
    echo "  python scripts/test_piper.py"
}

# Main
echo "============================================"
echo "  Descargador de modelos Piper TTS"
echo "============================================"

if [ $# -eq 0 ]; then
    print_warning "No se especificó ningún modelo"
    show_models
    echo ""
    read -p "Ingresa el nombre del modelo a descargar (o presiona Enter para el recomendado): " MODEL_INPUT
    
    if [ -z "$MODEL_INPUT" ]; then
        MODEL_INPUT="sharvard-medium"
        print_info "Usando modelo recomendado: $MODEL_INPUT"
    fi
    
    download_model "$MODEL_INPUT"
else
    download_model "$1"
fi

print_success "¡Proceso completado!"
