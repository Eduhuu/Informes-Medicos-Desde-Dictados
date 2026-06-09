import {
  AUDIO_BYTES_PER_SAMPLE,
  AUDIO_FILE_FRAME_DURATION_MS,
  AUDIO_SAMPLE_RATE,
} from '../../constants/AudioConstants';

const SAMPLES_PER_FRAME = Math.floor((AUDIO_SAMPLE_RATE * AUDIO_FILE_FRAME_DURATION_MS) / 1000);
const BYTES_PER_FRAME = SAMPLES_PER_FRAME * AUDIO_BYTES_PER_SAMPLE;

/**
 * Emulates the interface of PcmAudioCaptureService but feeds frames from a
 * pre-loaded PCM Uint8Array instead of the microphone.
 *
 * Frames are emitted synchronously so the VAD can process the full file in one
 * pass before the caller sends SESSION_END.
 */
export class PcmAudioFileSource {
  constructor() {
    this.onFrame = null;
    this.isPlaying = false;
  }

  /**
   * @param {Uint8Array} pcmBytes - raw PCM s16le bytes extracted from a WAV file
   * @param {function(Uint8Array): void} onFrame - callback for each PCM frame
   */
  start(pcmBytes, onFrame) {
    if (this.isPlaying) {
      return;
    }

    this.onFrame = onFrame;
    this.isPlaying = true;

    let offset = 0;

    while (offset + BYTES_PER_FRAME <= pcmBytes.length) {
      const frame = pcmBytes.slice(offset, offset + BYTES_PER_FRAME);
      this.onFrame(frame);
      offset += BYTES_PER_FRAME;
    }

    const remaining = pcmBytes.length - offset;
    if (remaining > 0) {
      const lastFrame = new Uint8Array(BYTES_PER_FRAME);
      lastFrame.set(pcmBytes.slice(offset));
      this.onFrame(lastFrame);
    }

    this.stop();
  }

  stop() {
    this.isPlaying = false;
    this.onFrame = null;
  }

  get playing() {
    return this.isPlaying;
  }
}
