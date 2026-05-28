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

## PLN (extracción de entidades)

El servicio ejecuta dos modelos en **paralelo** tras cada transcripción con texto:

- **`pln_medical`**: NER médico general (p. ej. `rigonsallauka/spanish_medical_ner`).
- **`pln_farmacos`**: terminología farmacológica (p. ej. `PlanTL-GOB-ES/bsc-bio-ehr-es-pharmaconer`).

Ejemplo en `config.yaml`:

```yaml
pln_medical:
  task: ner
  model: rigonsallauka/spanish_medical_ner
  aggregation_strategy: max

pln_farmacos:
  task: token-classification
  model: PlanTL-GOB-ES/bsc-bio-ehr-es-pharmaconer
  aggregation_strategy: simple
```

**Fusión de entidades:** si ambos modelos detectan el mismo intervalo de texto, se conserva solo la entidad de `pln_farmacos`. Las entidades médicas que no solapan con fármacos se mantienen. En reportes y logs cada entidad indica su origen (`PLN médico` o `PLN fármacos`).

**Migración:** la clave antigua `pln` en el YAML se interpreta como `pln_medical` si no existe `pln_medical`.

Variables de entorno: `PLN_MEDICAL_TASK`, `PLN_MEDICAL_MODEL`, `PLN_MEDICAL_AGGREGATION_STRATEGY`, `PLN_FARMACOS_TASK`, `PLN_FARMACOS_MODEL`, `PLN_FARMACOS_AGGREGATION_STRATEGY` (y los legacy `PLN_TASK`, `PLN_MODEL`, `PLN_AGGREGATION_STRATEGY` para el bloque médico).

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

Cuando hay texto transcrito, el pipeline ejecuta ambos PLN y enriquece las entidades fusionadas con SNOMED CT (si `snomed.enabled` es `true`). Los reportes de sesión y los logs de consola incluyen el origen PLN de cada entidad.

## SNOMED CT (Snowstorm)

El servicio consulta Snowstorm por cada entidad detectada por el PLN. Levanta Snowstorm desde la raíz del repositorio:

```bash
docker compose -f snomed/docker-compose.yml up -d
```

Prueba directa de la API:

```bash
curl "http://localhost:8080/MAIN/SNOMEDCT-ES/concepts?term=EPOC&active=true&preferredLanguage=es&limit=3"
```

Configuración en `config.yaml` (solo activar o desactivar):

```yaml
snomed:
  enabled: true
```

El resto de parámetros (URL, rama, límite, etc.) usan los valores por defecto de `shared/constants/SnomedConstants`. Para sobreescribirlos sin tocar el YAML: `SNOMED_PROVIDER`, `SNOMED_BASE_URL`, `SNOMED_BRANCH`, `SNOMED_LIMIT`, `SNOMED_ACTIVE`, `SNOMED_PREFERRED_LANGUAGE`, `SNOMED_TIMEOUT_SECONDS`.

Con `SNOMED_PROVIDER=mock` no hace falta Snowstorm. Si Snowstorm no responde, cada entidad devuelve `snomed.items` vacío y `snomed.error` con un mensaje en español; el resto de la transcripción sigue disponible.

### Campo `entities`

Cada elemento combina la salida NER (`word`, `score`, `entity_group`, `start`, `end`, `pln_source`) con `snomed`, que replica la respuesta paginada de Snowstorm (`items`, `total`, `limit`, `offset`, `searchAfter`, `searchAfterArray`) más `error` cuando falla la consulta. El campo `pln_source` indica si la entidad proviene de `pln_medical` o `pln_farmacos`.
