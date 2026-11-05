from dotenv import load_dotenv

load_dotenv()

import json
import wave
from pathlib import Path

from google.cloud import speech

AUDIO_PATH = Path("audio/chapter-01.wav")
OUTPUT_PATH = Path(__file__).resolve().parent / "timestamps.json"
LANGUAGE_CODE = "en-US"


def main():
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(
            f"Áudio não encontrado: {AUDIO_PATH.resolve()}"
        )

    with wave.open(str(AUDIO_PATH), "rb") as audio_file:
        duration = audio_file.getnframes() / audio_file.getframerate()

    if duration > 60:
        raise ValueError(
            "Este script aceita WAV de até 60 segundos. "
            "Para áudios maiores, use a API assíncrona "
            "com Google Cloud Storage."
        )

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(
        content=AUDIO_PATH.read_bytes()
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=LANGUAGE_CODE,
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
    )

    response = client.recognize(
        config=config,
        audio=audio,
    )

    timestamps = []

    for result in response.results:
        for word in result.alternatives[0].words:
            timestamps.append({
                "word": word.word,
                "start": round(
                    word.start_time.total_seconds(), 3
                ),
                "end": round(
                    word.end_time.total_seconds(), 3
                ),
            })

    OUTPUT_PATH.write_text(
        json.dumps(timestamps, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"{len(timestamps)} palavras identificadas.")
    print(f"Arquivo gerado: {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
