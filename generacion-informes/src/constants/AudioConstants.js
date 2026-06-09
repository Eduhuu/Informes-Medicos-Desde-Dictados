export const AUDIO_SAMPLE_RATE = 16000;
export const AUDIO_CHANNELS = 1;
export const AUDIO_BIT_DEPTH = 16;
export const AUDIO_BYTES_PER_SAMPLE = 2;

export const AUDIO_FORMAT_PCM_S16LE = 'pcm_s16le';

export const VAD_WINDOW_MS = 30;
export const VAD_SILENCE_DURATION_MS = 600;
export const VAD_MIN_SPEECH_MS = 200;
export const VAD_ENERGY_THRESHOLD = 0.015;

export const VAD_STATE_SILENCE = 'silence';
export const VAD_STATE_SPEECH = 'speech';

export const AUDIO_EVENT_ON_DATA = 'onAudioData';

export const AUDIO_FILE_FRAME_DURATION_MS = VAD_WINDOW_MS;
