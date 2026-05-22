import ExpoAudioStream from 'expo-audio-stream-pcm';

import {
  AUDIO_BIT_DEPTH,
  AUDIO_CHANNELS,
  AUDIO_EVENT_ON_DATA,
  AUDIO_SAMPLE_RATE,
} from '../../constants/AudioConstants';
import { base64ToUint8Array } from '../../utils/pcmUtils';

export class PcmAudioCaptureService {
  constructor() {
    this.subscription = null;
    this.onFrame = null;
    this.isCapturing = false;
  }

  start(onFrame) {
    if (this.isCapturing) {
      return;
    }

    this.onFrame = onFrame;
    this.subscription = ExpoAudioStream.addListener(
      AUDIO_EVENT_ON_DATA,
      this.handleAudioData,
    );

    ExpoAudioStream.start({
      sampleRate: AUDIO_SAMPLE_RATE,
      channels: AUDIO_CHANNELS,
      bitDepth: AUDIO_BIT_DEPTH,
    });

    this.isCapturing = true;
  }

  handleAudioData = (event) => {
    if (!this.onFrame || !event?.data) {
      return;
    }

    const pcmBytes = base64ToUint8Array(event.data);
    this.onFrame(pcmBytes);
  };

  stop() {
    if (!this.isCapturing) {
      return;
    }

    ExpoAudioStream.stop();

    if (this.subscription) {
      this.subscription.remove();
      this.subscription = null;
    }

    this.onFrame = null;
    this.isCapturing = false;
  }

  get capturing() {
    return this.isCapturing;
  }
}
