import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  getRecordingPermissionsAsync,
  requestRecordingPermissionsAsync,
} from 'expo-audio';
import * as Crypto from 'expo-crypto';

import { VAD_STATE_SPEECH } from '../constants/AudioConstants';
import {
  WS_CONNECTION_STATE_CONNECTED,
  WS_CONNECTION_STATE_CONNECTING,
  WS_CONNECTION_STATE_DISCONNECTED,
  WS_CONNECTION_STATE_ERROR,
} from '../constants/WebSocketConstants';
import { AudioChunkAssembler } from '../services/audio/AudioChunkAssembler';
import { PcmAudioCaptureService } from '../services/audio/PcmAudioCaptureService';
import { VoiceActivityDetector } from '../services/audio/VoiceActivityDetector';
import { AudioStreamWebSocketClient } from '../services/websocket/AudioStreamWebSocketClient';

const PERMISSION_GRANTED = 'granted';
const PERMISSION_DENIED = 'denied';
const PERMISSION_PENDING = 'pending';

export function useAudioCaptureSession() {
  const captureServiceRef = useRef(new PcmAudioCaptureService());
  const vadRef = useRef(new VoiceActivityDetector());
  const assemblerRef = useRef(null);
  const websocketRef = useRef(new AudioStreamWebSocketClient());
  const sessionStartedAtRef = useRef(null);
  const durationIntervalRef = useRef(null);

  const [permissionStatus, setPermissionStatus] = useState(PERMISSION_PENDING);
  const [isRecording, setIsRecording] = useState(false);
  const [connectionState, setConnectionState] = useState(
    WS_CONNECTION_STATE_DISCONNECTED,
  );
  const [sessionId, setSessionId] = useState(null);
  const [chunksEmitted, setChunksEmitted] = useState(0);
  const [lastChunkDurationMs, setLastChunkDurationMs] = useState(0);
  const [sessionDurationSec, setSessionDurationSec] = useState(0);
  const [energyLevel, setEnergyLevel] = useState(0);
  const [voiceState, setVoiceState] = useState('silence');
  const [errorMessage, setErrorMessage] = useState(null);

  const stopDurationTimer = useCallback(() => {
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = null;
    }
  }, []);

  const startDurationTimer = useCallback(() => {
    stopDurationTimer();
    sessionStartedAtRef.current = Date.now();

    durationIntervalRef.current = setInterval(() => {
      const elapsedMs = Date.now() - sessionStartedAtRef.current;
      setSessionDurationSec(Math.floor(elapsedMs / 1000));
    }, 1000);
  }, [stopDurationTimer]);

  useEffect(() => {
    websocketRef.current.setStateChangeHandler(setConnectionState);

    const loadPermissionStatus = async () => {
      try {
        const { granted, status } = await getRecordingPermissionsAsync();

        if (granted) {
          setPermissionStatus(PERMISSION_GRANTED);
          return;
        }

        setPermissionStatus(
          status === 'undetermined' ? PERMISSION_PENDING : PERMISSION_DENIED,
        );
      } catch (error) {
        setPermissionStatus(PERMISSION_DENIED);
      }
    };

    loadPermissionStatus();

    return () => {
      stopDurationTimer();
      captureServiceRef.current.stop();
      websocketRef.current.disconnect();
    };
  }, [stopDurationTimer]);

  const requestPermission = useCallback(async () => {
    setPermissionStatus(PERMISSION_PENDING);

    try {
      const { granted } = await requestRecordingPermissionsAsync();
      setPermissionStatus(granted ? PERMISSION_GRANTED : PERMISSION_DENIED);
      return granted;
    } catch (error) {
      setPermissionStatus(PERMISSION_DENIED);
      setErrorMessage('No se pudo acceder al micrófono');
      return false;
    }
  }, []);

  const emitChunk = useCallback((chunkEvent, options = {}) => {
    if (!assemblerRef.current || !chunkEvent?.pcmBytes?.length) {
      return;
    }

    const metadata = assemblerRef.current.createChunkMetadata(
      chunkEvent.pcmBytes,
      {
        durationMs: chunkEvent.durationMs,
        isFinal: options.isFinal ?? false,
      },
    );

    websocketRef.current.sendChunk(metadata, chunkEvent.pcmBytes);

    setChunksEmitted((current) => current + 1);
    setLastChunkDurationMs(chunkEvent.durationMs);

    if (__DEV__) {
      console.log('[AudioChunk]', metadata);
    }
  }, []);

  const handlePcmFrame = useCallback(
    (pcmBytes) => {
      const result = vadRef.current.processFrame(pcmBytes);

      setEnergyLevel(result.energy);
      setVoiceState(result.voiceState);

      for (const chunkEvent of result.events) {
        emitChunk(chunkEvent);
      }
    },
    [emitChunk],
  );

  const startSession = useCallback(async () => {
    setErrorMessage(null);

    const granted =
      permissionStatus === PERMISSION_GRANTED
        ? true
        : await requestPermission();

    if (!granted) {
      return;
    }

    const nextSessionId = Crypto.randomUUID();
    assemblerRef.current = new AudioChunkAssembler(nextSessionId);
    vadRef.current.reset();

    setSessionId(nextSessionId);
    setChunksEmitted(0);
    setLastChunkDurationMs(0);
    setSessionDurationSec(0);
    setEnergyLevel(0);
    setVoiceState('silence');

    await websocketRef.current.connect();

    captureServiceRef.current.start(handlePcmFrame);
    startDurationTimer();
    setIsRecording(true);
  }, [handlePcmFrame, permissionStatus, requestPermission, startDurationTimer]);

  const stopSession = useCallback(() => {
    const pendingChunk = vadRef.current.flushPendingSpeech();

    if (pendingChunk) {
      emitChunk(pendingChunk, { isFinal: true });
    }

    captureServiceRef.current.stop();
    stopDurationTimer();
    setIsRecording(false);
    setVoiceState('silence');
    setEnergyLevel(0);

    if (assemblerRef.current) {
      const sessionEndMetadata = assemblerRef.current.createSessionEndMetadata(
        assemblerRef.current.currentSequence,
      );
      websocketRef.current.sendSessionEnd(sessionEndMetadata);
    }

    websocketRef.current.disconnect();
  }, [emitChunk]);

  const connectionLabel = useMemo(() => {
    switch (connectionState) {
      case WS_CONNECTION_STATE_CONNECTED:
        return 'connected';
      case WS_CONNECTION_STATE_CONNECTING:
        return 'connecting';
      case WS_CONNECTION_STATE_ERROR:
        return 'error';
      default:
        return 'disconnected';
    }
  }, [connectionState]);

  const isSpeaking = voiceState === VAD_STATE_SPEECH;

  return {
    permissionStatus,
    isRecording,
    connectionState: connectionLabel,
    sessionId,
    chunksEmitted,
    lastChunkDurationMs,
    sessionDurationSec,
    energyLevel,
    isSpeaking,
    errorMessage,
    requestPermission,
    startSession,
    stopSession,
  };
}
