/** In-memory accumulator of PCM audio chunks per session for batch processing mode. */

const sessionBuffers = new Map();

/**
 * @param {string} sessionId
 * @param {Buffer} buffer
 * @param {object} metadata  - WebSocket chunk metadata (only the first one is kept)
 */
function addChunk(sessionId, buffer, metadata) {
    if (!sessionBuffers.has(sessionId)) {
        sessionBuffers.set(sessionId, { buffers: [], firstMetadata: metadata });
    }

    sessionBuffers.get(sessionId).buffers.push(buffer);
}

/**
 * Concatenates all accumulated buffers for the session, removes the entry, and returns
 * the combined audio together with the metadata from the first chunk.
 *
 * @param {string} sessionId
 * @returns {{ audioBuffer: Buffer, metadata: object } | null}
 */
function flushSession(sessionId) {
    const entry = sessionBuffers.get(sessionId);
    if (!entry) {
        return null;
    }

    const audioBuffer = Buffer.concat(entry.buffers);
    const { firstMetadata } = entry;

    sessionBuffers.delete(sessionId);

    return { audioBuffer, metadata: firstMetadata };
}

/**
 * Discards accumulated buffers for the session without processing them.
 * @param {string} sessionId
 */
function clearSession(sessionId) {
    sessionBuffers.delete(sessionId);
}

module.exports = {
    addChunk,
    flushSession,
    clearSession,
};
