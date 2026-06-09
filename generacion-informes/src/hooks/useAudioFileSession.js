import { useCallback, useEffect, useRef, useState } from 'react';
import * as DocumentPicker from 'expo-document-picker';
import * as Crypto from 'expo-crypto';

import {
  WS_CONNECTION_STATE_CONNECTED,
  WS_CONNECTION_STATE_CONNECTING,
  WS_CONNECTION_STATE_DISCONNECTED,
  WS_CONNECTION_STATE_ERROR,
} from '../constants/WebSocketConstants';
import { AudioChunkAssembler } from '../services/audio/AudioChunkAssembler';
import { PcmAudioFileSource } from '../services/audio/PcmAudioFileSource';
import { VoiceActivityDetector } from '../services/audio/VoiceActivityDetector';
import { readWavFile } from '../services/audio/WavFileReader';
import { AudioStreamWebSocketClient } from '../services/websocket/AudioStreamWebSocketClient';

const FILE_STATUS_IDLE = 'idle';
const FILE_STATUS_SENDING = 'sending';
const FILE_STATUS_SENT = 'sent';
const FILE_STATUS_ERROR = 'error';

const WAV_MIME_TYPE = 'audio/wav';
const WAV_MIME_TYPE_X = 'audio/x-wav';

export { FILE_STATUS_IDLE, FILE_STATUS_SENDING, FILE_STATUS_SENT, FILE_STATUS_ERROR };

export function useAudioFileSession() {
  const websocketRef = useRef(new AudioStreamWebSocketClient());
  const isSendingRef = useRef(false);

  const [loadedFiles, setLoadedFiles] = useState([]);
  const [connectionState, setConnectionState] = useState(WS_CONNECTION_STATE_DISCONNECTED);
  const [globalError, setGlobalError] = useState(null);

  useEffect(() => {
    websocketRef.current.setStateChangeHandler(setConnectionState);

    return () => {
      websocketRef.current.disconnect();
    };
  }, []);

  const updateFileStatus = useCallback((id, status, errorMessage = null) => {
    setLoadedFiles((current) =>
      current.map((file) =>
        file.id === id ? { ...file, status, errorMessage } : file,
      ),
    );
  }, []);

  const pickFile = useCallback(async () => {
    setGlobalError(null);

    const result = await DocumentPicker.getDocumentAsync({
      type: [WAV_MIME_TYPE, WAV_MIME_TYPE_X],
      copyToCacheDirectory: true,
      multiple: false,
    });

    if (result.canceled) {
      return;
    }

    const asset = result.assets[0];

    setLoadedFiles((current) => [
      ...current,
      {
        id: Crypto.randomUUID(),
        name: asset.name,
        uri: asset.uri,
        sizeBytes: asset.size ?? 0,
        status: FILE_STATUS_IDLE,
        errorMessage: null,
      },
    ]);
  }, []);

  const sendFile = useCallback(
    async (id) => {
      if (isSendingRef.current) {
        return;
      }

      const file = loadedFiles.find((f) => f.id === id);

      if (!file) {
        return;
      }

      isSendingRef.current = true;
      setGlobalError(null);
      updateFileStatus(id, FILE_STATUS_SENDING);

      const sessionId = Crypto.randomUUID();
      const assembler = new AudioChunkAssembler(sessionId);
      const vad = new VoiceActivityDetector();
      const fileSource = new PcmAudioFileSource();

      try {
        const pcmBytes = await readWavFile(file.uri);

        await websocketRef.current.connect();

        const emitChunk = (chunkEvent, options = {}) => {
          if (!chunkEvent?.pcmBytes?.length) {
            return;
          }

          const metadata = assembler.createChunkMetadata(chunkEvent.pcmBytes, {
            durationMs: chunkEvent.durationMs,
            isFinal: options.isFinal ?? false,
          });

          websocketRef.current.sendChunk(metadata, chunkEvent.pcmBytes);
        };

        const handlePcmFrame = (frame) => {
          const result = vad.processFrame(frame);

          for (const chunkEvent of result.events) {
            emitChunk(chunkEvent);
          }
        };

        fileSource.start(pcmBytes, handlePcmFrame);

        const pendingChunk = vad.flushPendingSpeech();

        if (pendingChunk) {
          emitChunk(pendingChunk, { isFinal: true });
        }

        const sessionEndMetadata = assembler.createSessionEndMetadata(assembler.currentSequence);
        websocketRef.current.sendSessionEnd(sessionEndMetadata);

        updateFileStatus(id, FILE_STATUS_SENT);
      } catch (error) {
        const message = error?.message ?? 'Error desconocido al enviar el archivo';
        updateFileStatus(id, FILE_STATUS_ERROR, message);
        setGlobalError(message);
      } finally {
        isSendingRef.current = false;
        websocketRef.current.disconnect();
      }
    },
    [loadedFiles, updateFileStatus],
  );

  const removeFile = useCallback((id) => {
    setLoadedFiles((current) => current.filter((file) => file.id !== id));
  }, []);

  const connectionLabel = (() => {
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
  })();

  const isSending = loadedFiles.some((f) => f.status === FILE_STATUS_SENDING);

  return {
    loadedFiles,
    connectionState: connectionLabel,
    isSending,
    globalError,
    pickFile,
    sendFile,
    removeFile,
  };
}
