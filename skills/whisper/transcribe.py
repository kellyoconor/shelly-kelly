#!/usr/bin/env python3
"""Transcribe audio files using OpenAI Whisper (local, free)."""
import sys, json, warnings
warnings.filterwarnings("ignore")

def transcribe(path, model_name="base"):
    import whisper
    model = whisper.load_model(model_name)
    result = model.transcribe(path)
    return result["text"].strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: transcribe.py <audio_file> [model]")
        sys.exit(1)
    path = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "base"
    text = transcribe(path, model)
    print(text)
