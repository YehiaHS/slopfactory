"""TTS via Mistral Voice API. Uses Mistral's voice generation for Reddit narration."""

import hashlib
import io
from pathlib import Path
from mistralai import Mistral
from config import settings


def get_client() -> Mistral:
    if not settings.mistral_api_key:
        raise ValueError("Mistral API key not configured — set SLOP_MISTRAL_API_KEY in .env")
    return Mistral(api_key=settings.mistral_api_key)


def generate_tts_audio(text: str, voice_id: str = "voice_troll") -> Path:
    """
    Generate TTS audio from Mistral. Returns path to wav file.
    The voice_troll model is the new voice model from Mistral.
    """
    client = get_client()
    output_dir = Path(settings.output_dir) / "tts"
    output_dir.mkdir(parents=True, exist_ok=True)

    text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
    output_path = output_dir / f"tts_{text_hash}.wav"
    if output_path.exists():
        return output_path

    # Split text into sentences for efficient chunking
    sentences = _split_sentences(text)

    # Generate audio for all sentence chunks in parallel
    audio_chunks = []
    for sentence in sentences:
        if not sentence.strip():
            continue
        resp = client.audio.speech.create(
            model="mistral-large-2-vt",
            input=sentence.strip(),
            voice=voice_id,
            response_format="wav",
        )
        audio_chunks.append(resp)

    # Concatenate all audio chunks
    output_path = _merge_audio_chunks(audio_chunks, output_path)
    return output_path


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences for efficient TTS chunking."""
    sentences = []
    current = ""
    for char in text:
        current += char
        if char in ".!?":
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())
    return sentences


def _merge_audio_chunks(chunks: list, output_path: Path) -> Path:
    """Merge multiple audio chunks into a single WAV file."""
    if len(chunks) == 1:
        with open(output_path, "wb") as f:
            f.write(chunks[0])
        return output_path

    try:
        from pydub import AudioSegment
        combined = AudioSegment.empty()
        for chunk in chunks:
            combined += AudioSegment.from_wav(io.BytesIO(chunk))
        combined.export(str(output_path), format="wav")
    except ImportError:
        # Fallback: use subprocess ffmpeg to concatenate
        import subprocess
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as td:
            paths = []
            for i, chunk in enumerate(chunks):
                p = os.path.join(td, f"chunk_{i}.wav")
                with open(p, "wb") as f:
                    f.write(chunk)
                paths.append(p)
            concat_file = os.path.join(td, "concat.txt")
            with open(concat_file, "w") as f:
                for p in paths:
                    f.write(f"file '{p}'\n")
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", str(output_path)],
                capture_output=True, check=True,
            )

    return output_path


# Available Mistral voices
AVAILABLE_VOICES = [
    {"id": "voice_troll", "name": "Troll", "description": "The signature Mistral voice"},
    {"id": "coral", "name": "Coral", "description": "Warm and engaging"},
    {"id": "lena", "name": "Lena", "description": "Professional and clear"},
    {"id": "mike", "name": "Mike", "description": "Deep and authoritative"},
    {"id": "thomas", "name": "Thomas", "description": "Friendly and conversational"},
]
