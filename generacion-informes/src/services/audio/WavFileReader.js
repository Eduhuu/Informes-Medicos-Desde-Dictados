import { File } from 'expo-file-system';

import {
  AUDIO_BYTES_PER_SAMPLE,
  AUDIO_CHANNELS,
  AUDIO_SAMPLE_RATE,
} from '../../constants/AudioConstants';
import { UI_FILE_INVALID_FORMAT } from '../../constants/UiStrings';

const WAV_RIFF_OFFSET = 0;
const WAV_WAVE_OFFSET = 8;
const WAV_FMT_OFFSET = 12;
const WAV_AUDIO_FORMAT_OFFSET = 20;
const WAV_NUM_CHANNELS_OFFSET = 22;
const WAV_SAMPLE_RATE_OFFSET = 24;
const WAV_BITS_PER_SAMPLE_OFFSET = 34;
const WAV_DATA_CHUNK_SEARCH_START = 36;

const WAV_RIFF_MAGIC = 'RIFF';
const WAV_WAVE_MAGIC = 'WAVE';
const WAV_FMT_MAGIC = 'fmt ';
const WAV_DATA_MAGIC = 'data';
const WAV_PCM_FORMAT = 1;

const EXPECTED_BITS_PER_SAMPLE = AUDIO_BYTES_PER_SAMPLE * 8;

function readFourCC(view, offset) {
  return String.fromCharCode(
    view.getUint8(offset),
    view.getUint8(offset + 1),
    view.getUint8(offset + 2),
    view.getUint8(offset + 3),
  );
}

function validateWavHeader(view) {
  const riff = readFourCC(view, WAV_RIFF_OFFSET);
  const wave = readFourCC(view, WAV_WAVE_OFFSET);
  const fmt = readFourCC(view, WAV_FMT_OFFSET);

  if (riff !== WAV_RIFF_MAGIC || wave !== WAV_WAVE_MAGIC || fmt !== WAV_FMT_MAGIC) {
    throw new Error(UI_FILE_INVALID_FORMAT);
  }

  const audioFormat = view.getUint16(WAV_AUDIO_FORMAT_OFFSET, true);
  const numChannels = view.getUint16(WAV_NUM_CHANNELS_OFFSET, true);
  const sampleRate = view.getUint32(WAV_SAMPLE_RATE_OFFSET, true);
  const bitsPerSample = view.getUint16(WAV_BITS_PER_SAMPLE_OFFSET, true);

  if (
    audioFormat !== WAV_PCM_FORMAT ||
    numChannels !== AUDIO_CHANNELS ||
    sampleRate !== AUDIO_SAMPLE_RATE ||
    bitsPerSample !== EXPECTED_BITS_PER_SAMPLE
  ) {
    throw new Error(UI_FILE_INVALID_FORMAT);
  }
}

function findDataChunk(view) {
  let offset = WAV_DATA_CHUNK_SEARCH_START;

  while (offset + 8 <= view.byteLength) {
    const chunkId = readFourCC(view, offset);
    const chunkSize = view.getUint32(offset + 4, true);

    if (chunkId === WAV_DATA_MAGIC) {
      return { dataOffset: offset + 8, dataSize: chunkSize };
    }

    offset += 8 + chunkSize;
  }

  throw new Error(UI_FILE_INVALID_FORMAT);
}

/**
 * Reads a WAV file from the given URI, validates its format (16 kHz, mono, 16-bit PCM),
 * and returns the raw PCM bytes.
 *
 * @param {string} uri - expo-file-system compatible URI
 * @returns {Promise<Uint8Array>} raw PCM bytes (s16le)
 * @throws {Error} if the file is not a valid 16 kHz / mono / 16-bit WAV
 */
export async function readWavFile(uri) {
  const file = new File(uri);
  const bytes = await file.bytes();
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);

  validateWavHeader(view);

  const { dataOffset, dataSize } = findDataChunk(view);

  return bytes.slice(dataOffset, dataOffset + dataSize);
}
