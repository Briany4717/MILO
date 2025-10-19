import os
import sys
import torch
from TTS.api import TTS

"""Preload the Coqui TTS model specified by env var TTS_MODEL.
This script attempts to create the TTS object which will trigger the model download.
"""
MODEL = os.getenv('TTS_MODEL', 'tts_models/multilingual/multi-dataset/xtts_v2')

def main():
    print('Preloading TTS model:', MODEL)
    # Monkey-patch input to auto-accept the CPML license during build
    import builtins
    builtins.input = lambda *args, **kwargs: 'y'
    try:
        t = TTS(MODEL, progress_bar=False)
        print('TTS model instantiated, cache dir should contain the model')
    except Exception as e:
        print('Warning: failed to preload TTS model:', e)
        # Continue without failing the build to keep build resilient

if __name__ == '__main__':
    main()
