# Dockerfiles in this repository

This document explains the purpose of the Dockerfiles included in this repo and which one to use.

- `Dockerfile.gpu` — GPU-enabled image based on NVIDIA CUDA runtime. Use this when you have an NVIDIA GPU and want to run heavy TTS/STT models on the GPU. Requires NVIDIA drivers and NVIDIA Container Toolkit on the host.
- `Dockerfile.optimized.final` — CPU-optimized multi-stage image for production or for machines without GPU.
- Other Dockerfile.* — legacy or experimental Dockerfiles. Keep them for reference, but prefer the two above for reproducible builds.

Recommendation: keep `Dockerfile.gpu` and `Dockerfile.optimized.final` as the canonical builds, and archive or remove other Dockerfiles after verification.
