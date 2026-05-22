import {
  VAD_ENERGY_THRESHOLD,
  VAD_MIN_SPEECH_MS,
  VAD_SILENCE_DURATION_MS,
  VAD_STATE_SILENCE,
  VAD_STATE_SPEECH,
  VAD_WINDOW_MS,
} from '../../constants/AudioConstants';
import {
  calculateRmsEnergy,
  getSamplesPerWindow,
  pcmBytesToInt16Samples,
} from '../../utils/pcmUtils';

export class VoiceActivityDetector {
  constructor(options = {}) {
    this.energyThreshold = options.energyThreshold ?? VAD_ENERGY_THRESHOLD;
    this.silenceDurationThreshold =
      options.silenceDurationMs ?? VAD_SILENCE_DURATION_MS;
    this.minSpeechMs = options.minSpeechMs ?? VAD_MIN_SPEECH_MS;
    this.windowMs = options.windowMs ?? VAD_WINDOW_MS;

    this.samplesPerWindow = getSamplesPerWindow();
    this.sampleBuffer = [];
    this.pendingBytes = new Uint8Array(0);
    this.voiceState = VAD_STATE_SILENCE;
    this.speechDurationMs = 0;
    this.silenceDurationMs = 0;
    this.currentEnergy = 0;
  }

  reset() {
    this.sampleBuffer = [];
    this.pendingBytes = new Uint8Array(0);
    this.voiceState = VAD_STATE_SILENCE;
    this.speechDurationMs = 0;
    this.silenceDurationMs = 0;
    this.currentEnergy = 0;
  }

  processFrame(pcmBytes) {
    const mergedBytes = new Uint8Array(
      this.pendingBytes.length + pcmBytes.length,
    );
    mergedBytes.set(this.pendingBytes, 0);
    mergedBytes.set(pcmBytes, this.pendingBytes.length);

    const samples = pcmBytesToInt16Samples(mergedBytes);
    const consumedSampleCount =
      Math.floor(samples.length / this.samplesPerWindow) *
      this.samplesPerWindow;
    const consumedByteCount = consumedSampleCount * 2;
    this.pendingBytes = mergedBytes.slice(consumedByteCount);

    const events = [];

    for (
      let offset = 0;
      offset + this.samplesPerWindow <= samples.length;
      offset += this.samplesPerWindow
    ) {
      const windowSamples = samples.subarray(
        offset,
        offset + this.samplesPerWindow,
      );
      const windowEvent = this.processWindow(windowSamples);

      if (windowEvent) {
        events.push(windowEvent);
      }
    }

    return {
      events,
      energy: this.currentEnergy,
      voiceState: this.voiceState,
    };
  }

  processWindow(windowSamples) {
    this.currentEnergy = calculateRmsEnergy(windowSamples);
    const isSpeech = this.currentEnergy >= this.energyThreshold;

    if (isSpeech) {
      this.voiceState = VAD_STATE_SPEECH;
      this.speechDurationMs += this.windowMs;
      this.silenceDurationMs = 0;
      this.sampleBuffer.push(windowSamples);
      return null;
    }

    if (this.voiceState === VAD_STATE_SPEECH) {
      this.silenceDurationMs += this.windowMs;
      this.sampleBuffer.push(windowSamples);

      if (this.silenceDurationMs >= this.silenceDurationThreshold) {
        return this.buildChunkEvent();
      }

      return null;
    }

    this.voiceState = VAD_STATE_SILENCE;
    this.speechDurationMs = 0;
    this.silenceDurationMs = 0;
    return null;
  }

  buildChunkEvent() {
    if (this.speechDurationMs < this.minSpeechMs || this.sampleBuffer.length === 0) {
      this.resetSpeechBuffer();
      return null;
    }

    const chunkBytes = this.samplesToBytes(this.sampleBuffer);
    const durationMs = this.speechDurationMs + this.silenceDurationMs;

    this.resetSpeechBuffer();

    return {
      pcmBytes: chunkBytes,
      durationMs,
    };
  }

  flushPendingSpeech() {
    if (
      this.voiceState !== VAD_STATE_SPEECH ||
      this.speechDurationMs < this.minSpeechMs ||
      this.sampleBuffer.length === 0
    ) {
      this.resetSpeechBuffer();
      return null;
    }

    const chunkBytes = this.samplesToBytes(this.sampleBuffer);
    const durationMs = this.speechDurationMs + this.silenceDurationMs;

    this.resetSpeechBuffer();

    return {
      pcmBytes: chunkBytes,
      durationMs,
    };
  }

  resetSpeechBuffer() {
    this.sampleBuffer = [];
    this.voiceState = VAD_STATE_SILENCE;
    this.speechDurationMs = 0;
    this.silenceDurationMs = 0;
  }

  samplesToBytes(sampleWindows) {
    const totalSamples = sampleWindows.reduce(
      (sum, window) => sum + window.length,
      0,
    );
    const bytes = new Uint8Array(totalSamples * 2);
    const dataView = new DataView(bytes.buffer);

    let sampleOffset = 0;

    for (const window of sampleWindows) {
      for (let index = 0; index < window.length; index += 1) {
        dataView.setInt16(sampleOffset * 2, window[index], true);
        sampleOffset += 1;
      }
    }

    return bytes;
  }
}
