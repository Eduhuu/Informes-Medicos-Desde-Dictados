const {
    ASR_TRANSCRIBE_PATH,
    ASR_GENERATE_REPORT_PATH,
    ASR_BATCH_TIMEOUT_MS,
    CONTENT_TYPE_OCTET_STREAM,
    DEFAULT_ASR_SERVICE_URL,
    ENV_ASR_SERVICE_URL,
    HEADER_SEQUENCE,
    HEADER_SESSION_ID,
    HEADER_TIMESTAMP,
} = require('../../shared/constants/GatewayConstants/gatewayConstants');

function resolveAsrBaseUrl() {
    const configured = process.env[ENV_ASR_SERVICE_URL];
    const baseUrl = configured ?? DEFAULT_ASR_SERVICE_URL;
    return baseUrl.replace(/\/$/, '');
}

function isoTimestampToEpochMs(isoTimestamp) {
    if (!isoTimestamp) {
        return null;
    }

    const epochMs = Date.parse(isoTimestamp);
    if (Number.isNaN(epochMs)) {
        return null;
    }

    return String(epochMs);
}

function buildTranscribeHeaders(metadata) {
    const headers = {
        [HEADER_SESSION_ID]: metadata.sessionId,
        [HEADER_SEQUENCE]: String(metadata.sequence),
        'Content-Type': CONTENT_TYPE_OCTET_STREAM,
    };

    const timestampMs = isoTimestampToEpochMs(metadata.timestamp);
    if (timestampMs !== null) {
        headers[HEADER_TIMESTAMP] = timestampMs;
    }

    return headers;
}

async function _doFetch(url, fetchOptions) {
    const response = await fetch(url, fetchOptions);

    const responseBody = await response.text();
    let parsedBody = null;

    if (responseBody) {
        try {
            parsedBody = JSON.parse(responseBody);
        } catch {
            parsedBody = { detail: responseBody };
        }
    }

    if (!response.ok) {
        const detail =
            parsedBody?.detail ??
            parsedBody?.message ??
            `El servicio ASR respondió con código ${response.status}`;

        const error = new Error(
            typeof detail === 'string' ? detail : JSON.stringify(detail),
        );
        error.statusCode = response.status;
        throw error;
    }

    return parsedBody ?? {};
}

async function transcribeAudioChunk(audioBuffer, metadata, options = {}) {
    const url = `${resolveAsrBaseUrl()}${ASR_TRANSCRIBE_PATH}`;
    const headers = buildTranscribeHeaders(metadata);

    const fetchOptions = {
        method: 'POST',
        headers,
        body: audioBuffer,
    };

    if (options.batch) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), ASR_BATCH_TIMEOUT_MS);
        fetchOptions.signal = controller.signal;

        try {
            return await _doFetch(url, fetchOptions);
        } finally {
            clearTimeout(timeoutId);
        }
    }

    return _doFetch(url, fetchOptions);
}

async function generateReport(sessionId) {
    const url = `${resolveAsrBaseUrl()}${ASR_GENERATE_REPORT_PATH}/${sessionId}`;
    return _doFetch(url, { method: 'POST' });
}

module.exports = {
    transcribeAudioChunk,
    generateReport,
};
