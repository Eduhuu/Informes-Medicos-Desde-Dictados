const {
    JSON_MESSAGE_START_BYTE,
    WS_MESSAGE_TYPE_AUDIO_CHUNK,
    WS_MESSAGE_TYPE_SESSION_END,
    WS_RESPONSE_TYPE_ERROR,
    WS_RESPONSE_TYPE_SESSION_END,
    WS_RESPONSE_TYPE_FHIR_REPORT,
    WS_RESPONSE_TYPE_LLM_REPORT,
    WS_RESPONSE_TYPE_TRANSCRIPTION,
    DEFAULT_PROCESSING_MODE,
    PROCESSING_MODE_BATCH,
} = require('../../shared/constants/GatewayConstants/gatewayConstants');
const {
    transcribeAudioChunk,
    generateReport,
    generateFhirReport,
} = require('../services/asrTranscribeClient');
const { addChunk, flushSession, clearSession } = require('../services/batchAudioBuffer');

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

function resolveProcessingMode() {
    return DEFAULT_PROCESSING_MODE;
}

function attachAudioWebSocketHandlers(ws) {
    const processingMode = resolveProcessingMode();
    let pendingMetadata = null;

    ws.on('message', async (message) => {
        try {
            if (isJsonMessage(message)) {
                const metadata = parseMetadataMessage(message);

                if (metadata.type === WS_MESSAGE_TYPE_SESSION_END) {
                    pendingMetadata = null;

                    if (processingMode === PROCESSING_MODE_BATCH) {
                        await _handleBatchSessionEnd(ws, metadata);
                        return;
                    }

                    sendJson(ws, {
                        type: WS_RESPONSE_TYPE_SESSION_END,
                        message: 'Sesión finalizada correctamente',
                        sessionId: metadata.sessionId,
                    });

                    generateReport(metadata.sessionId)
                        .then((result) => {
                            sendJson(ws, {
                                type: WS_RESPONSE_TYPE_LLM_REPORT,
                                sessionId: metadata.sessionId,
                                report: result.report,
                            });
                        })
                        .catch((err) => {
                            if (err.statusCode === 503) {
                                console.log(
                                    `Generación de reporte LLM deshabilitada (sesión=${metadata.sessionId})`,
                                );
                                return;
                            }
                            console.error(
                                `Error al generar el reporte médico (sesión=${metadata.sessionId}):`,
                                err,
                            );
                            sendJson(ws, {
                                type: WS_RESPONSE_TYPE_ERROR,
                                message: `Error al generar el reporte médico: ${err.message ?? err}`,
                            });
                        })
                        .finally(() => {
                            generateFhirReport(metadata.sessionId)
                                .then((result) => {
                                    sendJson(ws, {
                                        type: WS_RESPONSE_TYPE_FHIR_REPORT,
                                        sessionId: metadata.sessionId,
                                        fhirReport: result.fhir_report,
                                    });
                                })
                                .catch((err) => {
                                    if (err.statusCode === 503) {
                                        console.log(
                                            `Generación de reporte FHIR deshabilitada (sesión=${metadata.sessionId})`,
                                        );
                                        return;
                                    }
                                    console.error(
                                        `Error al generar el reporte FHIR (sesión=${metadata.sessionId}):`,
                                        err,
                                    );
                                    sendJson(ws, {
                                        type: WS_RESPONSE_TYPE_ERROR,
                                        message: `Error al generar el reporte FHIR: ${err.message ?? err}`,
                                    });
                                });
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

            if (processingMode === PROCESSING_MODE_BATCH) {
                addChunk(metadata.sessionId, audioBuffer, metadata);
                console.log(
                    `Fragmento acumulado (sesión=${metadata.sessionId}, secuencia=${metadata.sequence}, bytes=${audioBuffer.length})`,
                );
                return;
            }

            console.log(
                `Fragmento recibido (sesión=${metadata.sessionId}, secuencia=${metadata.sequence}, bytes=${audioBuffer.length})`,
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

async function _handleBatchSessionEnd(ws, sessionEndMetadata) {
    const { sessionId } = sessionEndMetadata;
    const flushed = flushSession(sessionId);

    if (!flushed) {
        sendJson(ws, {
            type: WS_RESPONSE_TYPE_SESSION_END,
            message: 'Sesión finalizada. No se encontraron fragmentos de audio acumulados.',
            sessionId,
        });
        return;
    }

    const { audioBuffer, metadata: firstMetadata } = flushed;

    console.log(
        `Procesando audio batch (sesión=${sessionId}, bytes totales=${audioBuffer.length})`,
    );

    try {
        const transcription = await transcribeAudioChunk(audioBuffer, firstMetadata, { batch: true });

        sendJson(ws, {
            type: WS_RESPONSE_TYPE_TRANSCRIPTION,
            sessionId,
            sequence: firstMetadata.sequence,
            ...transcription,
        });
    } catch (error) {
        clearSession(sessionId);
        throw error;
    }
}

module.exports = {
    attachAudioWebSocketHandlers,
    resolveProcessingMode,
};
