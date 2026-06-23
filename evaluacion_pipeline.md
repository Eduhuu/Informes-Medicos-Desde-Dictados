# Evaluación end-to-end del pipeline ASR → NER → SNOMED/CIE-10 → Informe LLM → FHIR

**Casos analizados:** `backend/asr-service/reports/mode_batches/Test1` .. `Test10`
**Método:** comparación de `text.txt` (ground truth) contra `Reporte.txt`, `Informe.txt` y `Fhir_Reporte.json` por caso, en 5 dimensiones (1-5) + tiempo total.

## 1. Tabla resumen por caso

| Caso | ASR | NER | Terminología | Informe LLM | FHIR | Tiempo total |
|------|-----|-----|---------------|-------------|------|--------------|
| Test1  | 4 | 2 | 2 | 2 | 3 | 8.07 s |
| Test2  | 4 | 2 | 2 | 2 | 3 | 23.48 s |
| Test3  | 4 | 3 | 1 | 1 | 2 | 26.47 s |
| Test4  | 4 | 2 | 2 | 2 | 3 | 34.48 s |
| Test5  | 4 | 2 | 2 | 2 | 3 | 38.58 s |
| Test6  | 4 | 2 | 2 | 3 | 3 | 48.26 s |
| Test7  | 4 | 2 | 2 | 1 | 3 | 36.16 s |
| Test8  | 4 | 2 | 2 | 1 | 2 | 52.60 s |
| Test9  | 2 | 2 | 3 | 3 | 2 | 19.06 s |
| Test10 | 5 | 3 | 2 | 4 | 3 | 33.55 s |

## 2. Hallazgos por caso

**Test1** — ASR sólida (~97-98%) pero error de unidad peligroso "50 μg/h"→"50 miligramos hora" (no se propaga porque la dosis no se extrae). NER pierde "doloroso"/"analgesia" por completo (la ambigüedad señalada nunca se manifiesta porque el término ni se extrae). "hernia"→52515009 *Hernia of abdominal cavity* y CIE-10 K46.9 son anatómicamente incorrectos (caso es hernia discal/espinal, debería ser M51.x). Durogesic sin mapeo SNOMED. Informe.txt alucina diagnóstico **"Cefalea a estudio"** sin base alguna.

**Test2** — ASR ~96%; "TTG"→"CTG" (acrónimo de prueba de laboratorio mal transcrito). NER con falsos positivos en stopwords/puntuación; "DQ2/DQ8" (marcadores HLA) mal etiquetados como fármaco. "atrofia moderada"→771307003 *Charcot-Marie-Tooth type 2B5* (neuropatía, sin relación con atrofia vellositaria duodenal) + CIE-10 G60.0. Pierde la negación de "no fumador". Repite la alucinación **"Cefalea a estudio"**. FHIR modela DQ2/DQ8 como MedicationStatement (debería ser Observation).

**Test3** — peor caso de terminología: HTA→1260345007 *Headache due to arterial hypertension* (confunde hipertensión con cefalea); "zona"→*Herpes zoster*; "una"→*Nail structure* (mapea un artículo); "estenosante"→*Stenosing cholangitis* (órgano equivocado). 17/26 entidades sin CIE-10. **Fallo total del LLM**: Informe.txt no es un informe clínico sino una meta-descripción del propio pipeline NLP, sin diagnóstico ni anexo SNOMED útil. FHIR propaga fielmente toda la basura terminológica sin filtro.

**Test4** — ASR mangla el fármaco crítico "micofenolato-mofetil"→"micro fenol átomo fetil", perdiéndose el tratamiento de mantenimiento. NER con ~50% de spans ruido ("cuadro", "mala", "sesiones" como PROBLEM). "sangre afectación"→1264458000 *Acute undifferentiated leukemia* (severidad alucinada, el paciente no tiene leucemia); "mala"→*Entire zygoma* (dominio erróneo). Informe omite el tratamiento real al no recuperarse upstream.

**Test5** — "ni flare"→"nifler" (signo clínico perdido). NER no captura los diagnósticos centrales "AOC" y "DG" como entidades. Mapeos terminológicos absurdos: "amarillento"→422642000 *Brotogeris tirica* (una especie de loro); "cejas"→*Loss of eyebrows* (polaridad invertida). CIE-10 prácticamente 0/21 matches útiles. Informe.txt **alucina expansiones de siglas** ("AOC = Anomalía del Crecimiento Ocular", "DG = Degeneración") sin respaldo, y omite la sección de consanguinidad familiar.

**Test6** — "DLE" (drenaje lumbar externo)→"hundle"/"ley", el dispositivo nunca se identifica correctamente downstream. NER etiqueta stopwords ("un", "una", "alta") como PROBLEM. "alta"→248328003 *Tall stature* (confunde alta de hospital con estatura) y CIE-10 E34.4 erróneo. Informe.txt **inventa una sección de "Recursos Adicionales"** con referencias bibliográficas (OMS, NIA, AHA) sin base en el encuentro, y omite la narrativa real (complicación del DLE, hematoma, retirada).

**Test7** — ASR mangla términos clave: "auscultación cardio-respiratoria"→2 tokens rotos; "cistouretroscopía"→"lacisto uretroscopía" (irrecuperable). "un papiloma"→10236001 *Excision of intraductal papilloma of breast* (sitio anatómico y tipo equivocados: mama vs. uretra). Solo 3/27 entidades con CIE-10; el diagnóstico real (papiloma invertido de uretra) nunca recibe código. **Fallo del LLM**: Informe.txt es una meta-narración sobre la tabla de codificación ("no se encontró correspondencia..."), sin diagnóstico ni narrativa clínica.

**Test8** — corte de transcripción a mitad de frase (pierde "-yeyunal" de la anastomosis); "Billroth II"→"Bilrod 2". NER fragmenta "Ulcus Gástrico Péptico" en 4 entidades sueltas. "leve aumento"→702346005 *Potocki-Shaffer syndrome* (síndrome genético, sin relación); "infiltración neoplásica"→1264010001 *Primary hypereosinophilic syndrome* (diagnóstico equivocado) con CIE-10 D47.5 — riesgo de codificar mal una neoplasia. **Fallo del LLM**: respuesta confusa y autorreferencial sin narrativa de paciente. FHIR crea 4 MedicationStatement vacíos (analitos de laboratorio mal enrutados como medicación).

**Test9** — peor ASR del lote (~23% WER): "SDRC"→"DSDRC" (sigla del diagnóstico corrompida) y **alucinación de una lista de fármacos no presentes en el original** (Enalapril, Losartán, Omeprazol, Metformina, Atorvastatina) — parece audio-bleed de otra grabación. El pipeline enriquece correctamente estos fármacos fantasma con SNOMED válido, lo cual agrava el problema de precisión. El diagnóstico real (SDRC/CRPS) nunca se convierte en entidad ni recurso FHIR — omisión crítica. Informe.txt refleja fielmente la entrada corrupta sin señalar la implausibilidad clínica (un paciente de 13 años con 5 fármacos de adulto crónico).

**Test10** — mejor caso del lote: ASR casi perfecta (~0.6% WER), Informe.txt el más coherente y fiel (recoge neurofibromatosis tipo 1, glioma, plan de seguimiento, sin alucinaciones). Pese a ello, "neuroimagen"→1220600004 *RARS-related autosomal recessive hypomyelinating leukodystrophy* (enfermedad genética rara sin relación) propaga CIE-10 E75.2 erróneo al FHIR. "una resonancia"→*Magnetic resonance elastography* (modalidad equivocada). El diagnóstico "glioma del nervio óptico" se reduce a solo "glioma", perdiendo especificidad anatómica.

## 3. Hallazgos transversales

- **ASR es el eslabón fuerte y, a la vez, el cuello de botella temporal**: precisión consistente ~95-99% (excepto Test9, ~77%), pero representa el 60-84% del tiempo total de procesamiento en casi todos los casos.
- **La capa de terminología (SNOMED/CIE-10) es el eslabón más débil y sistemático**: realiza emparejamiento léxico sin contexto sobre tokens cortos o ambiguos (artículos, adjetivos sueltos, fragmentos), produciendo mapeos clínicamente absurdos y recurrentes — síndromes genéticos raros (Charcot-Marie-Tooth, Potocki-Shaffer, leucodistrofia), una especie de loro, "pérdida de cejas", "institución penal". Este patrón aparece en al menos 7 de los 10 casos.
- **NER tiene un problema doble y recurrente**: falsos positivos por etiquetar stopwords/artículos/adjetivos sueltos como PROBLEM o TREATMENT, y falsos negativos en diagnósticos/dispositivos/siglas clínicamente centrales (SDRC, DLE, AOC/DG, papiloma invertido), que terminan ausentes de SNOMED, del informe y del FHIR.
- **El LLM tiene dos modos de fallo recurrentes**: (a) alucinación de contenido no presente en la fuente — diagnóstico repetido **"Cefalea a estudio"** (Test1, Test2), expansión inventada de siglas (Test5), referencias bibliográficas fabricadas (Test6); (b) colapso total de la tarea, generando una meta-descripción del propio pipeline de codificación en vez de un informe clínico (Test3, Test7, Test8) — este segundo modo es el más grave porque deja al usuario sin informe utilizable.
- **El FHIR Bundle es estructuralmente sólido pero no filtra nada**: siempre bien formado (resourceType, profile, subject) y trazable 1:1 a Reporte.txt, pero hereda sin control todos los errores de NER/terminología — entidades ruido convertidas en Condition formales, fármacos fantasma convertidos en MedicationStatement, recursos de laboratorio mal tipados como medicación (Test8).
- **La ambigüedad "doloroso"/"analgesia" señalada como riesgo en Test1 no se observó directamente** porque NER nunca llega a extraer esos términos — el riesgo está enmascarado, no resuelto, por un fallo de recall anterior en la cadena.
- **Caso atípico de integridad de datos**: Test9 muestra una posible contaminación cruzada de audio (lista de fármacos de otro paciente insertada en la transcripción), un problema de origen distinto a los anteriores y potencialmente más grave por motivos de seguridad del paciente.

## 4. Métricas agregadas

- **WER medio (ASR):** ≈ 3-5% en 9/10 casos; Test9 es un outlier con ≈23%. Media aproximada del lote (excluyendo outlier): ~3%; incluyendo Test9: ~5-6%.
- **Precisión/Recall NER (estimado):** precisión moderada-baja por exceso de falsos positivos (stopwords, fragmentos, adjetivos sueltos etiquetados); recall moderado-bajo por omisión sistemática de siglas, dispositivos y diagnósticos completos. Ningún caso alcanza una extracción limpia 1:1 con el ground truth.
- **% entidades sin mapeo SNOMED/CIE-10:** rango muy amplio entre casos, desde ~0% hasta ~65% sin correspondencia (Test5, Test3 con tasas muy altas); media estimada del lote en torno al 30-40%.
- **% de casos con alucinación o fallo grave en el Informe LLM:** 8/10 casos (Test1, Test2, Test3, Test5, Test6, Test7, Test8, Test9) presentan alucinación de contenido o colapso de la tarea; solo Test4 y Test10 están razonablemente libres de estos problemas (Test10 es el único caso limpio en este aspecto).
- **Tiempo medio total:** ≈ 32.1 s por caso (rango 8.1 s – 52.6 s), con ASR representando consistentemente la mayor parte (60-84%) del tiempo.

## 5. Recomendaciones priorizadas

1. **Filtrar y validar NER antes de enriquecer**: descartar stopwords/artículos/fragmentos de un solo carácter como candidatos a entidad, y mejorar el recall sobre siglas, dispositivos y diagnósticos compuestos (HTA, SDRC, DLE, AOC/DG). Esto es la causa raíz de la mayoría de errores downstream.
2. **Añadir un filtro de coherencia semántica en la capa SNOMED/CIE-10**: rechazar o marcar como baja confianza mapeos cuyo dominio clínico (p. ej. especie animal, síndrome genético raro, anatomía no relacionada) sea incompatible con el contexto de la nota, en vez de aceptar el primer match léxico.
3. **Endurecer el prompt/validación del LLM generador del Informe**: detectar y rechazar salidas que no sigan la estructura clínica esperada (caso de "colapso total" en Test3/7/8), y restringir explícitamente la generación a hechos presentes en las entidades/códigos de entrada para evitar alucinaciones (diagnósticos inventados, siglas expandidas sin base, referencias bibliográficas fabricadas).
4. **Investigar el caso de contaminación de audio en Test9** como posible defecto de pipeline de captura/segmentación de audio — tiene implicaciones de seguridad del paciente (fármacos no prescritos apareciendo en el registro).
5. **Optimizar la latencia de ASR**, ya que domina el tiempo total en casi todos los casos; en menor medida, investigar por qué el tiempo de SNOMED en Test6 es anómalamente alto respecto al número de entidades (posible latencia del servidor de terminología, no escalado por volumen).
6. **Añadir trazabilidad de confianza/origen hasta el FHIR Bundle**: actualmente el Bundle hereda fielmente cualquier error upstream sin marcar baja confianza, lo que dificulta auditar después qué codificaciones merecen revisión clínica manual.
