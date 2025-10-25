#!/usr/bin/env python3
"""End-to-end test: STT -> LLM (no-stream) -> TTS

This script is intended to be executed inside the project container (GPU or CPU).
It reads a sample file from `samples/`, transcribes it with Whisper, asks the LLM
for a response (non-streaming), and synthesizes it to `response_e2e.wav`.
"""
import traceback
from pathlib import Path

WORKDIR = Path(__file__).resolve().parent
SAMPLE = WORKDIR / 'samples' / 'alejandro_sample_v2.wav'
OUT_WAV = WORKDIR / 'response_e2e.wav'

def safe_extract_content(resp):
    """Try several common response shapes to get the assistant text."""
    try:
        # OpenAI-like response object with choices
        if hasattr(resp, 'choices') and len(resp.choices) > 0:
            choice = resp.choices[0]
            # handle .message.content
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                return choice.message.content
            # handle .text
            if hasattr(choice, 'text'):
                return choice.text
        # dict-like
        if isinstance(resp, dict):
            if 'choices' in resp and len(resp['choices']) > 0:
                c = resp['choices'][0]
                if isinstance(c, dict) and 'message' in c and isinstance(c['message'], dict):
                    return c['message'].get('content', str(resp))
            # fallback: if it's already a content string
            if 'content' in resp:
                return resp['content']
        # fallback to str
        return str(resp)
    except Exception:
        return str(resp)

def main():
    print('E2E test start')
    try:
        from src import stt_processor, llm_processor, tts_processor
        # Transcribe
        print('Transcribing sample:', SAMPLE)
        text = stt_processor.stt_processor.transcribe(str(SAMPLE)) if hasattr(stt_processor, 'stt_processor') else stt_processor.transcribe(str(SAMPLE))
        print('Transcription:', text[:300])

        # LLM request (non-stream)
        print('Requesting LLM (no-stream)')
        try:
            resp = llm_processor.llm_processor.client.chat.completions.create(
                model=llm_processor.llm_processor.model,
                messages=llm_processor.llm_processor.history + [{'role':'user','content': text}],
                stream=False,
            )
        except Exception as e:
            print('LLM call failed:', e)
            traceback.print_exc()
            resp = {'content': 'Lo siento, no puedo contactar al LLM en este momento.'}

        content = safe_extract_content(resp)
        print('LLM response:', content[:500])

        # Use content directly (no JSON parsing needed)
        mensaje = content.strip()
        print('Message to synthesize (truncated):', mensaje[:200])

        # TTS: split into sentences and synthesize sequentially to reduce peak GPU memory
        print('Splitting mensaje into sentences and synthesizing sequentially to avoid OOM')
        try:
            sentences = tts_processor.tts_processor.split_into_sentences(mensaje) if hasattr(tts_processor, 'tts_processor') else tts_processor.split_into_sentences(mensaje)
        except Exception:
            # fallback: single chunk
            sentences = [mensaje]

        tmp_files = []
        from scipy.io import wavfile
        import numpy as np

        for i, s in enumerate(sentences):
            tmp_path = WORKDIR / f'tmp_tts_{i}.wav'
            print(f'  Synthesizing sentence {i+1}/{len(sentences)}: "{s[:80]}..."')
            try:
                if hasattr(tts_processor, 'tts_processor'):
                    tts_processor.tts_processor.generate_audio(s, str(tmp_path))
                else:
                    tts_processor.generate_audio(s, str(tmp_path))
                tmp_files.append(tmp_path)
            except Exception as e:
                print('  Failed to synthesize sentence:', e)
                # try to free CUDA memory and continue
                try:
                    import torch
                    torch.cuda.empty_cache()
                except Exception:
                    pass

        if not tmp_files:
            raise RuntimeError('No TTS outputs were produced')

        # Concatenate WAVs
        print('Concatenating', len(tmp_files), 'wav parts into', OUT_WAV)
        sample_rate = None
        data_parts = []
        for f in tmp_files:
            sr, data = wavfile.read(str(f))
            if sample_rate is None:
                sample_rate = sr
            elif sample_rate != sr:
                raise RuntimeError('Sample rate mismatch between tmp wav parts')
            # ensure mono
            if data.ndim > 1:
                data = data.mean(axis=1).astype(data.dtype)
            data_parts.append(data)

        full = np.concatenate(data_parts, axis=0)
        wavfile.write(str(OUT_WAV), sample_rate, full)
        print('WAV produced at', OUT_WAV)

        # Cleanup tmp files
        for f in tmp_files:
            try:
                f.unlink()
            except Exception:
                pass

    except Exception as e:
        print('E2E test failed:', e)
        traceback.print_exc()

if __name__ == '__main__':
    main()
