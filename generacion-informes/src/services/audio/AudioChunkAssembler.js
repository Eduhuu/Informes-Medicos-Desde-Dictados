import {
  AUDIO_CHANNELS,
  AUDIO_FORMAT_PCM_S16LE,
  AUDIO_SAMPLE_RATE,
} from '../../constants/AudioConstants';
import { WS_MESSAGE_TYPE_AUDIO_CHUNK, WS_MESSAGE_TYPE_SESSION_END } from '../../constants/WebSocketConstants';

export class AudioChunkAssembler {
  constructor(sessionId) {
    this.sessionId = sessionId;
    this.sequence = 0;
  }

  createChunkMetadata(pcmBytes, options = {}) {
    const durationMs = options.durationMs ?? 0;
    const metadata = {
      type: WS_MESSAGE_TYPE_AUDIO_CHUNK,
      sessionId: this.sessionId,
      sequence: this.sequence,
      timestamp: new Date().toISOString(),
      format: AUDIO_FORMAT_PCM_S16LE,
      sampleRate: AUDIO_SAMPLE_RATE,
      channels: AUDIO_CHANNELS,
      durationMs,
      byteLength: pcmBytes.length,
      isFinal: options.isFinal ?? false,
    };

    this.sequence += 1;

    return metadata;
  }

  createSessionEndMetadata(totalChunks) {
    return {
      type: WS_MESSAGE_TYPE_SESSION_END,
      sessionId: this.sessionId,
      totalChunks,
      timestamp: new Date().toISOString(),
    };
  }

  get currentSequence() {
    return this.sequence;
  }
}
