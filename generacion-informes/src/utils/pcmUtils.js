import {
  AUDIO_BYTES_PER_SAMPLE,
  AUDIO_SAMPLE_RATE,
  VAD_WINDOW_MS,
} from '../constants/AudioConstants';

export function base64ToUint8Array(base64Data) {
  const binaryString = atob(base64Data);
  const bytes = new Uint8Array(binaryString.length);

  for (let index = 0; index < binaryString.length; index += 1) {
    bytes[index] = binaryString.charCodeAt(index);
  }

  return bytes;
}

export function pcmBytesToInt16Samples(pcmBytes) {
  const sampleCount = Math.floor(pcmBytes.length / AUDIO_BYTES_PER_SAMPLE);
  const samples = new Int16Array(sampleCount);
  const dataView = new DataView(
    pcmBytes.buffer,
    pcmBytes.byteOffset,
    pcmBytes.byteLength,
  );

  for (let index = 0; index < sampleCount; index += 1) {
    samples[index] = dataView.getInt16(index * AUDIO_BYTES_PER_SAMPLE, true);
  }

  return samples;
}

export function calculateRmsEnergy(samples) {
  if (samples.length === 0) {
    return 0;
  }

  let sumSquares = 0;

  for (let index = 0; index < samples.length; index += 1) {
    const normalizedSample = samples[index] / 32768;
    sumSquares += normalizedSample * normalizedSample;
  }

  return Math.sqrt(sumSquares / samples.length);
}

export function getSamplesPerWindow() {
  return Math.floor((AUDIO_SAMPLE_RATE * VAD_WINDOW_MS) / 1000);
}

export function getDurationMsFromByteLength(byteLength) {
  const sampleCount = byteLength / AUDIO_BYTES_PER_SAMPLE;
  return Math.round((sampleCount / AUDIO_SAMPLE_RATE) * 1000);
}

export function concatUint8Arrays(chunks) {
  const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
  const merged = new Uint8Array(totalLength);
  let offset = 0;

  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }

  return merged;
}
