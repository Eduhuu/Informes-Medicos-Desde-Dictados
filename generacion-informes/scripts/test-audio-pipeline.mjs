const AUDIO_SAMPLE_RATE = 16000;
const AUDIO_BYTES_PER_SAMPLE = 2;
const VAD_WINDOW_MS = 30;
const VAD_SILENCE_DURATION_MS = 600;
const VAD_MIN_SPEECH_MS = 200;
const VAD_ENERGY_THRESHOLD = 0.015;
const VAD_STATE_SILENCE = 'silence';
const VAD_STATE_SPEECH = 'speech';

function pcmBytesToInt16Samples(pcmBytes) {
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

function calculateRmsEnergy(samples) {
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

function getSamplesPerWindow() {
  return Math.floor((AUDIO_SAMPLE_RATE * VAD_WINDOW_MS) / 1000);
}

class VoiceActivityDetector {
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

    return { events };
  }

  processWindow(windowSamples) {
    const currentEnergy = calculateRmsEnergy(windowSamples);
    const isSpeech = currentEnergy >= this.energyThreshold;

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

    const durationMs = this.speechDurationMs + this.silenceDurationMs;
    const totalSamples = this.sampleBuffer.reduce(
      (sum, window) => sum + window.length,
      0,
    );

    this.resetSpeechBuffer();

    return {
      pcmBytes: new Uint8Array(totalSamples * 2),
      durationMs,
    };
  }

  resetSpeechBuffer() {
    this.sampleBuffer = [];
    this.voiceState = VAD_STATE_SILENCE;
    this.speechDurationMs = 0;
    this.silenceDurationMs = 0;
  }
}

function createTonePcmBytes(durationMs, frequencyHz = 440, amplitude = 0.5) {
  const sampleCount = Math.floor((AUDIO_SAMPLE_RATE * durationMs) / 1000);
  const bytes = new Uint8Array(sampleCount * AUDIO_BYTES_PER_SAMPLE);
  const dataView = new DataView(bytes.buffer);

  for (let index = 0; index < sampleCount; index += 1) {
    const sampleValue = Math.sin((2 * Math.PI * frequencyHz * index) / AUDIO_SAMPLE_RATE);
    const int16Value = Math.round(sampleValue * amplitude * 32767);
    dataView.setInt16(index * AUDIO_BYTES_PER_SAMPLE, int16Value, true);
  }

  return bytes;
}

function createSilencePcmBytes(durationMs) {
  const sampleCount = Math.floor((AUDIO_SAMPLE_RATE * durationMs) / 1000);
  return new Uint8Array(sampleCount * AUDIO_BYTES_PER_SAMPLE);
}

function runVadScenario() {
  const vad = new VoiceActivityDetector({
    energyThreshold: 0.01,
    silenceDurationMs: 300,
    minSpeechMs: 200,
  });

  const frameDurationMs = VAD_WINDOW_MS * 4;
  const speechFrame = createTonePcmBytes(frameDurationMs, 440, 0.8);
  const silenceFrame = createSilencePcmBytes(frameDurationMs);
  const emittedChunks = [];

  for (let index = 0; index < 8; index += 1) {
    emittedChunks.push(...vad.processFrame(speechFrame).events);
  }

  for (let index = 0; index < 12; index += 1) {
    emittedChunks.push(...vad.processFrame(silenceFrame).events);
  }

  if (emittedChunks.length !== 1) {
    throw new Error(`Expected 1 chunk, received ${emittedChunks.length}`);
  }

  if (emittedChunks[0].durationMs <= 0) {
    throw new Error('Chunk duration must be greater than zero');
  }
}

try {
  runVadScenario();
  console.log('Audio pipeline tests passed');
} catch (error) {
  console.error('Audio pipeline tests failed:', error.message);
  process.exit(1);
}
