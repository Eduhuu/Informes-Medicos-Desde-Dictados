import {
  WS_CONNECT_TIMEOUT_MS,
  WS_CONNECTION_STATE_CONNECTED,
  WS_CONNECTION_STATE_CONNECTING,
  WS_CONNECTION_STATE_DISCONNECTED,
  WS_CONNECTION_STATE_ERROR,
  WS_DEFAULT_URL,
  WS_MESSAGE_TYPE_SESSION_END,
  WS_RECONNECT_ATTEMPTS,
} from '../../constants/WebSocketConstants';

export class AudioStreamWebSocketClient {
  constructor(options = {}) {
    this.url = options.url ?? process.env.EXPO_PUBLIC_WS_URL ?? WS_DEFAULT_URL;
    this.reconnectAttempts = options.reconnectAttempts ?? WS_RECONNECT_ATTEMPTS;
    this.connectTimeoutMs = options.connectTimeoutMs ?? WS_CONNECT_TIMEOUT_MS;
    this.socket = null;
    this.connectionState = WS_CONNECTION_STATE_DISCONNECTED;
    this.onStateChange = null;
    this.pendingChunks = [];
  }

  setStateChangeHandler(handler) {
    this.onStateChange = handler;
  }

  setConnectionState(state) {
    this.connectionState = state;

    if (this.onStateChange) {
      this.onStateChange(state);
    }
  }

  connect() {
    if (
      this.connectionState === WS_CONNECTION_STATE_CONNECTED ||
      this.connectionState === WS_CONNECTION_STATE_CONNECTING
    ) {
      return Promise.resolve(this.connectionState);
    }

    this.setConnectionState(WS_CONNECTION_STATE_CONNECTING);

    return new Promise((resolve) => {
      let attemptsUsed = 0;

      const tryConnect = () => {
        this.closeSocket();

        try {
          this.socket = new WebSocket(this.url);
        } catch (error) {
          this.setConnectionState(WS_CONNECTION_STATE_ERROR);
          resolve(WS_CONNECTION_STATE_ERROR);
          return;
        }

        const timeoutId = setTimeout(() => {
          this.handleConnectionFailure(attemptsUsed, tryConnect, resolve);
          attemptsUsed += 1;
        }, this.connectTimeoutMs);

        this.socket.onopen = () => {
          clearTimeout(timeoutId);
          this.setConnectionState(WS_CONNECTION_STATE_CONNECTED);
          this.flushPendingChunks();
          resolve(WS_CONNECTION_STATE_CONNECTED);
        };

        this.socket.onerror = () => {
          clearTimeout(timeoutId);
          this.handleConnectionFailure(attemptsUsed, tryConnect, resolve);
          attemptsUsed += 1;
        };

        this.socket.onclose = () => {
          if (this.connectionState === WS_CONNECTION_STATE_CONNECTED) {
            this.setConnectionState(WS_CONNECTION_STATE_DISCONNECTED);
          }
        };
      };

      tryConnect();
    });
  }

  handleConnectionFailure(attemptsUsed, tryConnect, resolve) {
    this.closeSocket();

    if (attemptsUsed < this.reconnectAttempts) {
      tryConnect();
      return;
    }

    this.setConnectionState(WS_CONNECTION_STATE_ERROR);
    resolve(WS_CONNECTION_STATE_ERROR);
  }

  sendChunk(metadata, pcmBytes) {
    const payload = {
      metadata,
      pcmBytes,
    };

    if (this.connectionState !== WS_CONNECTION_STATE_CONNECTED || !this.socket) {
      this.pendingChunks.push(payload);
      return false;
    }

    try {
      this.socket.send(JSON.stringify(metadata));
      this.socket.send(pcmBytes);
      return true;
    } catch (error) {
      this.pendingChunks.push(payload);
      this.setConnectionState(WS_CONNECTION_STATE_ERROR);
      return false;
    }
  }

  sendSessionEnd(metadata) {
    if (this.connectionState !== WS_CONNECTION_STATE_CONNECTED || !this.socket) {
      return false;
    }

    try {
      this.socket.send(JSON.stringify(metadata));
      return true;
    } catch (error) {
      this.setConnectionState(WS_CONNECTION_STATE_ERROR);
      return false;
    }
  }

  flushPendingChunks() {
    if (!this.socket || this.connectionState !== WS_CONNECTION_STATE_CONNECTED) {
      return;
    }

    const queuedChunks = [...this.pendingChunks];
    this.pendingChunks = [];

    for (const chunk of queuedChunks) {
      this.socket.send(JSON.stringify(chunk.metadata));
      this.socket.send(chunk.pcmBytes);
    }
  }

  disconnect() {
    this.pendingChunks = [];
    this.closeSocket();
    this.setConnectionState(WS_CONNECTION_STATE_DISCONNECTED);
  }

  closeSocket() {
    if (!this.socket) {
      return;
    }

    this.socket.onopen = null;
    this.socket.onerror = null;
    this.socket.onclose = null;

    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.close();
    }

    this.socket = null;
  }

  get state() {
    return this.connectionState;
  }

  get isConnected() {
    return this.connectionState === WS_CONNECTION_STATE_CONNECTED;
  }
}

export { WS_MESSAGE_TYPE_SESSION_END };
