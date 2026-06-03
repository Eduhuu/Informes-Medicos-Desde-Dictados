/** In-memory accumulator of enriched entities per session (from ASR transcribe responses). */

const {
    TRANSCRIBE_RESPONSE_KEY_ENTITIES,
} = require('../../shared/constants/GatewayConstants/gatewayConstants');

const sessionEntities = new Map();

/**
 * @param {string} sessionId
 * @param {object[]} entities
 */
function appendEntities(sessionId, entities) {
    if (!sessionId || !Array.isArray(entities) || entities.length === 0) {
        return;
    }

    if (!sessionEntities.has(sessionId)) {
        sessionEntities.set(sessionId, []);
    }

    sessionEntities.get(sessionId).push(...entities);
}

/**
 * @param {string} sessionId
 * @param {object} transcription - ASR /transcribe JSON body
 */
function appendFromTranscription(sessionId, transcription) {
    const entities = transcription?.[TRANSCRIBE_RESPONSE_KEY_ENTITIES];
    appendEntities(sessionId, entities);
}

/**
 * Returns a deduplicated flat list (same word + span kept once).
 * @param {string} sessionId
 * @returns {object[]}
 */
function getEntities(sessionId) {
    const accumulated = sessionEntities.get(sessionId) ?? [];
    const seen = new Set();
    const deduplicated = [];

    for (const entity of accumulated) {
        const key = `${entity.start}:${entity.end}:${entity.word}`;
        if (seen.has(key)) {
            continue;
        }
        seen.add(key);
        deduplicated.push(entity);
    }

    return deduplicated;
}

/**
 * @param {string} sessionId
 */
function clearSessionEntities(sessionId) {
    sessionEntities.delete(sessionId);
}

module.exports = {
    appendEntities,
    appendFromTranscription,
    getEntities,
    clearSessionEntities,
};
