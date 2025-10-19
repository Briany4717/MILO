"""Smoke check for CI: verifies that critical imports succeed and a lightweight CPU-only instantiation works.

This is intended to run in CI on a small runner (no GPU). It should be fast and not download large models.
"""
import sys
import importlib

REQUIRED = [
    "torch",
    "TTS.api",
    "faster_whisper",
]


def check_import(name):
    try:
        importlib.import_module(name)
        print(f"OK import {name}")
        return True
    except Exception as e:
        print(f"FAILED import {name}: {e}")
        return False


def main():
    ok = True
    for r in REQUIRED:
        ok = check_import(r) and ok

    # quick torch check
    try:
        import torch

        print(f"torch.cuda.is_available: {torch.cuda.is_available()}")
        x = torch.zeros(1)
        print("torch zeros on CPU OK")
    except Exception as e:
        print("Torch CPU check failed:", e)
        ok = False

    if not ok:
        sys.exit(2)


if __name__ == "__main__":
    main()
