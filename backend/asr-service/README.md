# ASR Service

Microservicio de transcripción por fragmentos de audio. El motor activo se selecciona por configuración (`config.yaml` o variables de entorno) sin cambiar el contrato de la API.

## Arranque rápido

```bash
cd asr-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml   # si aún no existe
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Cambiar de motor (Whisper ↔ otro)

1. Edita `config.yaml`:

```yaml
asr:
  provider: whisper   # mock | whisper (+ futuros proveedores)
  model: base
  device: cpu         # cuda si tienes GPU
  language: es
  compute_type: int8
```

2. Reinicia el servicio. La factory precarga el modelo al arrancar.

Variables de entorno equivalentes: `ASR_PROVIDER`, `ASR_MODEL`, `ASR_DEVICE`, `ASR_LANGUAGE`, `ASR_COMPUTE_TYPE`, `ASR_CONFIG_PATH`.

## Añadir un nuevo proveedor

1. Crea `app/providers/mi_proveedor.py` implementando `ASRProvider` (`transcribe`, `health_check`, `get_metadata`, opcional `preload`).
2. Registra el identificador en `shared/constants/AsrConstants/asr_constants.py`.
3. Añade el caso en `app/factory/asr_factory.py`.

## API

### `POST /transcribe`

- **Body:** PCM 16-bit mono 16 kHz (binario).
- **Cabeceras opcionales:** `X-Session-Id`, `X-Sequence`, `X-Timestamp` (ms).

```bash
curl -X POST http://localhost:8001/transcribe \
  -H "Content-Type: application/octet-stream" \
  -H "X-Session-Id: consulta-001" \
  -H "X-Sequence: 0" \
  --data-binary @fragmento.pcm
```

### `GET /health` · `GET /metadata`

Estado del motor y metadatos para métricas del TFM (motor, versión, dispositivo).

## Contrato de salida

Todos los proveedores devuelven el mismo esquema: `text`, `segments`, `confidence`, `engine`, `model_version`, `device`, `latency_ms`, `session_id`, `sequence`.
