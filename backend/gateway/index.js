const {resolveProcessingMode} = require('./handlers/audioWebSocketHandler');
const express = require('express');
const http = require('http');
const { WebSocketServer } = require('ws');

const { DEFAULT_GATEWAY_PORT } = require('../shared/constants/GatewayConstants/gatewayConstants');
const { attachAudioWebSocketHandlers } = require('./handlers/audioWebSocketHandler');

const app = express();
const PORT = Number(process.env.GATEWAY_PORT) || DEFAULT_GATEWAY_PORT;

app.get('/', (req, res) => {
    res.send('Servidor de Audio HTTP funcionando 🎧');
});

const server = http.createServer(app);

const ws = new WebSocketServer({ server, path: '/audio' });

ws.on('connection', (ws, req) => {
    const ip = req.socket.remoteAddress;
    console.log(`✅ Cliente conectado desde la IP: ${ip}`);

    attachAudioWebSocketHandlers(ws);

    ws.on('close', () => {
        console.log('❌ Cliente desconectado');
    });

    ws.on('error', (error) => {
        console.error('Error en el socket:', error);
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Servidor escuchando en http://0.0.0.0:${PORT}`);
    console.log(`🔌 WebSocket disponible en ws://<IP-de-tu-PC>:${PORT}/audio`);
    console.log(`🌐 En tu red local usa la IP de tu PC, ej: 192.168.0.100:${PORT}`);
    console.log(`🔍 Processing mode: ${resolveProcessingMode()}`);
});
