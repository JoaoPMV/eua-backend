"""
Forced alignment local (torchaudio MMS_FA) para áudios longos.

Usa o TEXTO ORIGINAL + o áudio e gera timestamps.json:
[{"sentence": "...", "start": 0.0, "end": 1.2}, ...]

Dependências:
    pip install torch torchaudio numpy soundfile

Obs.: na primeira execução, o modelo é baixado automaticamente.
"""

import json
import math
import re
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio


AUDIO_PATH = Path("audio/eua-chapter-02.wav")

TEXT = """
Hello! Today, I will tell you about my family. My family lives in the United States. My mother is 56 years old. She is from Scotland, but she moved to the United States when she was 20 years old. She likes her life in America, but she still loves Scottish food and music. She is a kind and friendly person. She works at a local supermarket and enjoys cooking for the family. My father is American. He was born in the United States, but he doesn't live there anymore. My parents are divorced, and my father moved to France a few years ago. He enjoys living in Europe and learning about French culture. We don't see each other very often, but we talk on the phone sometimes. I have two sisters. My older sister is 32 years old, and her name is Emily. She is a teacher at a local school. My younger sister is 24 years old, and her name is Olivia. She works at a coffee shop and loves listening to music. We are a close family, and we enjoy spending time together. I sometimes call them on weekends because I miss them a lot. I also like sharing photos of my life in Norway with them. Even though we live in different countries, my family is always important to me!
"""

OUTPUT_PATH = Path(__file__).resolve().parent / "timestamps.json"

START_PADDING = 0.10
END_PADDING = 0.15

SEGMENT_END = re.compile(r"[,.;:!?]$")

CHUNK_SECONDS = 30
CONTEXT_SECONDS = 1
STRIDE = 320


def load_audio(path, target_sr):
    """Carrega WAV com SoundFile, converte para mono e 16 kHz."""

    audio, sr = sf.read(
        str(path),
        dtype="float32",
        always_2d=True
    )

    # Converte canais para mono
    audio = audio.mean(axis=1)

    waveform = torch.from_numpy(audio).unsqueeze(0)

    # Reamostragem, se necessário
    if sr != target_sr:
        waveform = torchaudio.functional.resample(
            waveform,
            orig_freq=sr,
            new_freq=target_sr
        )

    return waveform


@torch.inference_mode()
def compute_emission(model, waveform, sample_rate, device):
    """Calcula as emissões em janelas para suportar áudios longos."""

    total = waveform.size(1)
    chunk = CHUNK_SECONDS * sample_rate
    ctx = CONTEXT_SECONDS * sample_rate
    ctx_frames = ctx // STRIDE

    pieces = []

    for start in range(0, total, chunk):

        end = min(start + chunk, total)

        seg_start = max(0, start - ctx)
        seg_end = min(total, end + ctx)

        segment = waveform[:, seg_start:seg_end].to(device)

        emission, _ = model(segment)
        emission = emission[0]

        lead = ctx_frames if start > 0 else 0

        n_frames = math.ceil((end - start) / STRIDE)

        pieces.append(
            emission[lead:lead + n_frames].cpu()
        )

    emission = torch.cat(pieces, dim=0).unsqueeze(0)

    return torch.log_softmax(emission, dim=-1)


def normalize(word):
    """O modelo reconhece letras a-z e apóstrofo."""

    return re.sub(r"[^a-z']", "", word.lower())


def main():

    if not AUDIO_PATH.exists():
        raise FileNotFoundError(
            f"Áudio não encontrado: {AUDIO_PATH.resolve()}"
        )

    # Carrega áudio e identifica duração
    waveform = load_audio(
        AUDIO_PATH,
        torchaudio.pipelines.MMS_FA.sample_rate
    )

    duration = waveform.size(1) / torchaudio.pipelines.MMS_FA.sample_rate

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Dispositivo: {device}")
    print(f"Duração do áudio: {duration:.1f}s")

    # Carrega modelo MMS_FA
    print("Carregando modelo MMS_FA...")

    bundle = torchaudio.pipelines.MMS_FA

    model = bundle.get_model(with_star=False).to(device)
    dictionary = bundle.get_dict(star=None)

    sample_rate = bundle.sample_rate

    # Texto original separado em palavras
    original_words = re.findall(r"\S+", TEXT)

    aligned_idx = []
    token_ids = []

    for i, word in enumerate(original_words):

        norm = normalize(word)

        if not norm:
            print(
                f"Aviso: '{word}' não possui letras "
                "e não terá timestamp próprio."
            )
            continue

        missing = [c for c in norm if c not in dictionary]

        if missing:
            raise ValueError(
                f"Caracteres não encontrados no dicionário: {missing}"
            )

        aligned_idx.append(i)

        token_ids.append(
            [dictionary[c] for c in norm]
        )

    flat_targets = [
        token
        for word in token_ids
        for token in word
    ]

    if not flat_targets:
        raise RuntimeError("Nenhum caractere válido para alinhamento.")

    # Calcula emissões
    print("Calculando emissões do áudio...")

    emission = compute_emission(
        model,
        waveform,
        sample_rate,
        device
    )

    # Forced alignment
    print("Executando forced alignment...")

    targets = torch.tensor(
        [flat_targets],
        dtype=torch.int32
    )

    aligned, scores = torchaudio.functional.forced_align(
        emission,
        targets,
        blank=0
    )

    spans = torchaudio.functional.merge_tokens(
        aligned[0],
        scores[0].exp()
    )

    if len(spans) != len(flat_targets):
        raise RuntimeError(
            f"Alinhamento inconsistente: "
            f"{len(spans)} spans para "
            f"{len(flat_targets)} caracteres."
        )

    seconds_per_frame = (
        waveform.size(1) / emission.size(1)
    ) / sample_rate

    # Calcula timestamps individuais das palavras
    word_times = {}

    pos = 0

    for idx, ids in zip(aligned_idx, token_ids):

        word_spans = spans[pos:pos + len(ids)]

        pos += len(ids)

        word_times[idx] = (
            word_spans[0].start * seconds_per_frame,
            word_spans[-1].end * seconds_per_frame
        )

    # Agrupa palavras por pontuação
    timestamps = []

    current = []

    def flush():

        timed = [
            i for i in current
            if i in word_times
        ]

        if not timed:
            return

        start = word_times[timed[0]][0]
        end = word_times[timed[-1]][1]

        timestamps.append({
            "sentence": " ".join(
                original_words[i] for i in current
            ),
            "start": round(
                max(0, start - START_PADDING), 3
            ),
            "end": round(
                min(duration, end + END_PADDING), 3
            )
        })

    for i, word in enumerate(original_words):

        current.append(i)

        if SEGMENT_END.search(word):

            flush()
            current = []

    if current:
        flush()

    # Salva JSON
    OUTPUT_PATH.write_text(
        json.dumps(
            timestamps,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print()
    print(f"{len(timestamps)} segmentos identificados.")
    print(f"Duração do áudio: {duration:.1f}s")
    print(f"Arquivo gerado: {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()