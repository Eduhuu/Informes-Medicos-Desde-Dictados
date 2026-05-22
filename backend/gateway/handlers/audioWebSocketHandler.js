const {
    JSON_MESSAGE_START_BYTE,
    WS_MESSAGE_TYPE_AUDIO_CHUNK,
    WS_MESSAGE_TYPE_SESSION_END,
    WS_RESPONSE_TYPE_ERROR,
    WS_RESPONSE_TYPE_SESSION_END,
    WS_RESPONSE_TYPE_TRANSCRIPTION,
} = require('../../shared/constants/GatewayConstants/gatewayConstants');
const { transcribeAudioChunk } = require('../services/asrTranscribeClient');

function toBuffer(message) {
    if (Buffer.isBuffer(message)) {
        return message;
    }

    if (message instanceof ArrayBuffer) {
        return Buffer.from(message);
    }

    return Buffer.from(String(message));
}

function isJsonMessage(message) {
    const buffer = toBuffer(message);
    return buffer.length > 0 && buffer[0] === JSON_MESSAGE_START_BYTE;
}

function parseMetadataMessage(message) {
    const raw = toBuffer(message).toString('utf8');
    return JSON.parse(raw);
}

function sendJson(ws, payload) {
    ws.send(JSON.stringify(payload));
}

function attachAudioWebSocketHandlers(ws) {
    let pendingMetadata = null;

    ws.on('message', async (message) => {
        try {
            if (isJsonMessage(message)) {
                const metadata = parseMetadataMessage(message);

                if (metadata.type === WS_MESSAGE_TYPE_SESSION_END) {
                    pendingMetadata = null;
                    sendJson(ws, {
                        type: WS_RESPONSE_TYPE_SESSION_END,
                        message: 'Sesión finalizada correctamente',
                        sessionId: metadata.sessionId,
                    });
                    return;
                }

                if (metadata.type === WS_MESSAGE_TYPE_AUDIO_CHUNK) {
                    pendingMetadata = metadata;
                    return;
                }

                sendJson(ws, {
                    type: WS_RESPONSE_TYPE_ERROR,
                    message: `Tipo de mensaje no soportado: ${metadata.type}`,
                });
                return;
            }

            if (!pendingMetadata) {
                sendJson(ws, {
                    type: WS_RESPONSE_TYPE_ERROR,
                    message:
                        'Se recibió audio sin metadatos previos. Envía primero el JSON del fragmento.',
                });
                return;
            }

            const audioBuffer = toBuffer(message);
            const metadata = pendingMetadata;
            pendingMetadata = null;

            console.log(
                `🎙️ Fragmento recibido (sesión=${metadata.sessionId}, secuencia=${metadata.sequence}, bytes=${audioBuffer.length})`,
            );

            const transcription = await transcribeAudioChunk(audioBuffer, metadata);

            sendJson(ws, {
                type: WS_RESPONSE_TYPE_TRANSCRIPTION,
                sessionId: metadata.sessionId,
                sequence: metadata.sequence,
                ...transcription,
            });
        } catch (error) {
            pendingMetadata = null;
            console.error('Error al procesar mensaje WebSocket:', error);

            sendJson(ws, {
                type: WS_RESPONSE_TYPE_ERROR,
                message: error.message ?? 'Error al procesar el fragmento de audio',
            });
        }
    });
}

module.exports = {
    attachAudioWebSocketHandlers,
};
