#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<EOF
Usage: $0 [cpu|gpu]

Build helper for MILO Docker images.

Arguments:
    cpu   Build CPU-optimized image (default)
    gpu   Build GPU-enabled image (requires NVIDIA Container Toolkit)

Examples:
    $0 cpu
    $0 gpu
EOF
}

TARGET=${1:-cpu}
case "$TARGET" in
    cpu)
        echo "Building CPU image using Dockerfile.optimized.final"
        docker build -f Dockerfile.optimized.final -t milo-server:optimized .
        ;;
    gpu)
        echo "Building GPU image using Dockerfile.gpu"
        PRELOAD_TTS_ARG=""
        # Allow calling: ./smart-build.sh gpu preload-tts
        if [ "${2:-}" = "preload-tts" ] || [ "${PRELOAD_TTS:-0}" = "1" ]; then
            echo "-> Preloading TTS model during build (build-arg PRELOAD_TTS=1)"
            PRELOAD_TTS_ARG="--build-arg PRELOAD_TTS=1"
        fi
        docker build $PRELOAD_TTS_ARG -f Dockerfile.gpu -t milo-server:gpu .
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        echo "Unknown target: $TARGET" >&2
        usage
        exit 2
        ;;
esac
