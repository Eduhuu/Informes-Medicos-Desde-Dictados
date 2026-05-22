import numpy as np

from app.models.audio_chunk import AudioChunk


def chunk_to_float32_array(chunk: AudioChunk) -> np.ndarray:
    """Convert PCM 16-bit mono bytes to normalized float32 samples."""
    if chunk.sample_width_bytes != 2:
        raise ValueError(
            f"Unsupported sample width: {chunk.sample_width_bytes} bytes "
            "(only 16-bit PCM is supported)"
        )

    samples = np.frombuffer(chunk.data, dtype=np.int16)
    if chunk.channels > 1:
        samples = samples.reshape(-1, chunk.channels)[:, 0]

    return samples.astype(np.float32) / np.float32(32768.0)
