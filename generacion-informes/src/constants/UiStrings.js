export const UI_TITLE = 'Dictado clínico';
export const UI_START_RECORDING = 'Iniciar dictado';
export const UI_STOP_RECORDING = 'Detener dictado';
export const UI_PERMISSION_GRANTED = 'Permiso de micrófono concedido';
export const UI_PERMISSION_DENIED = 'Permiso de micrófono denegado';
export const UI_PERMISSION_PENDING = 'Solicitando permiso de micrófono…';
export const UI_RECORDING_ACTIVE = 'Grabando';
export const UI_RECORDING_IDLE = 'En espera';
export const UI_LISTENING = 'Escuchando…';
export const UI_PAUSE_DETECTED = 'Pausa detectada';
export const UI_SILENCE = 'Silencio';
export const UI_SESSION_DURATION = 'Duración de sesión';
export const UI_CHUNKS_EMITTED = 'Fragmentos emitidos';
export const UI_LAST_CHUNK_DURATION = 'Último fragmento';
export const UI_ENERGY_LEVEL = 'Nivel de voz';
export const UI_WS_DISCONNECTED = 'Desconectado';
export const UI_WS_CONNECTING = 'Conectando…';
export const UI_WS_CONNECTED = 'Conectado';
export const UI_WS_ERROR = 'Error de conexión';
export const UI_ERROR_MICROPHONE = 'No se pudo acceder al micrófono';
export const UI_ERROR_GENERIC = 'Ha ocurrido un error inesperado';
export const UI_MS_SUFFIX = 'ms';
export const UI_SECONDS_SUFFIX = 's';

export const UI_MODE_MICROPHONE = 'Micrófono';
export const UI_MODE_FILE = 'Archivo';

export const UI_SELECT_FILE = 'Seleccionar audio WAV';
export const UI_SEND_FILE = 'Enviar';
export const UI_REMOVE_FILE = 'Eliminar';

export const UI_FILE_STATUS_IDLE = 'Pendiente';
export const UI_FILE_STATUS_SENDING = 'Enviando…';
export const UI_FILE_STATUS_SENT = 'Enviado';
export const UI_FILE_STATUS_ERROR = 'Error';

export const UI_FILE_INVALID_FORMAT =
  'El archivo debe ser WAV 16 kHz, mono, 16 bits.\nConvierte con: ffmpeg -i entrada.wav -ar 16000 -ac 1 -sample_fmt s16 salida.wav';
export const UI_FILE_LIST_EMPTY = 'No hay archivos cargados. Pulsa "Seleccionar audio WAV" para añadir uno.';
