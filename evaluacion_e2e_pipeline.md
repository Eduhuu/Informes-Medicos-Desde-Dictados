# Evaluación E2E del pipeline ASR → NER → SNOMED/CIE-10 → Informe LLM → FHIR

Evaluación automática y reproducible de los 10 casos de prueba (Test1–Test10) para los dos modos de funcionamiento disponibles del sistema: **batches** y **streaming**, ubicados en `backend/asr-service/reports/end_to_end_tests/{batches,streaming}/testN`.

---

## 1. Tabla resumen — Modo `batches`

| Test | ASR | NER | Terminología | Informe LLM | FHIR | Tiempo total |
|---|---|---|---|---|---|---|
| test1 | 4 | 2 | 2 | 2 | 3 | 12.0 s |
| test2 | 2 | 2 | 1 | 2 | 3 | 23.9 s |
| test3 | 4 | 3 | 1 | 1 | 4 | 27.8 s |
| test4 | 3 | 2 | 1.5 | 1.5 | 2.5 | 33.8 s |
| test5 | 4 | 1.5 | 1 | 2 | 2.5 | 35.4 s |
| test6 | 3.5 | 2 | 1.5 | 2 | 2.5 | 43.4 s |
| test7 | 4 | 2 | 2 | 3 | 3 | 31.5 s |
| test8 | 4 | 2 | 1 | 1 | 2 | 44.7 s |
| test9\* | 4 | 2.5 | 3 | 2 | 3 | 18.9 s |
| test10 | 5 | 3 | 1 | 3 | 2 | 34.6 s |
| **Media** | **3.75** | **2.10** | **1.55** | **1.95** | **2.7** | **30.6 s** |

\* test9 recalculado: el `Reporte.txt` original incluía un fragmento de audio ajeno al caso (error de carga del evaluador, no del sistema) con 5 fármacos inexistentes (Enalapril, Losartán, Omeprazol, Metformina, Atorvastatina). Descontado ese fragmento, los errores reales del caso son la transcripción de "SDRC" como "DSDRC", su expansión incorrecta por el LLM como "Distrofia de Duchenne de Becker" y la pérdida de la negación sobre "traumatismo".

\*\* test1, test5 y test6 recalculados también en la columna "Informe LLM": el campo "Cefalea a estudio" no es una alucinación de plantilla sino el *fallback* explícito que el propio `system_prompt` del LLM (`backend/asr-service/config.yaml`) instruye usar para la Impresión Diagnóstica cuando el diagnóstico es ambiguo a partir del texto recibido. En estos tres casos el NER solo entrega al LLM una entidad de diagnóstico genérica o truncada (p. ej. "hernia" en vez de "hernia discal"), por lo que el *fallback* se activa por falta de información de entrada y no por una alucinación; persisten en estos casos otros errores reales independientes (dosis x1000 en test1, expansión de siglas inventada en test5, reproducción literal de "hundle" en test6) que justifican mantener una puntuación baja.

## 2. Tabla resumen — Modo `streaming`

| Test | ASR | NER | Terminología | Informe LLM | FHIR | Tiempo total |
|---|---|---|---|---|---|---|
| test1\*\* | 4 | 4 | 2 | 2 | 4 | 34.1 s |
| test2 | 4 | 3 | 2 | 3 | 4 | 101.2 s |
| test3 | 4 | 3 | 2 | 1 | 3 | 185.6 s |
| test4 | 4 | 3 | 2 | 3 | 3 | 157.4 s |
| test5 | 4 | 2 | 2 | 1 | 3 | 157.1 s |
| test6 | 4 | 2 | 2 | 1 | 3 | 412.8 s |
| test7 | 4 | 3 | 2 | 3 | 3 | 259.8 s |
| test8 | 4 | 3 | 1 | 2 | 2 | 127.3 s |
| test9 | 5 | 4 | 3 | 4 | 4 | 35.5 s |
| test10 | 4 | 2 | 1 | 2 | 3 | 378.2 s |
| **Media** | **4.0** | **2.9** | **1.9** | **2.2** | **3.2** | **184.9 s** |

\*\* test1 (streaming) recalculado en "Informe LLM": aquí el NER sí extrae correctamente "hernia discal" (mencionada incluso en el propio Motivo de Consulta del informe), pero el LLM no la traslada a la Impresión Diagnóstica y recurre al *fallback* "Cefalea a estudio" — a diferencia de los casos de `batches`, este es un fallo real de abstracción del LLM y no de información de entrada degradada. Mantiene puntuación baja porque además repite el error de dosis x1000 ("50 μg/h"→"50 mg/hora").

> Nota metodológica: en `streaming` los logs de Reporte.txt agregan varias secuencias por caso; las transcripciones y entidades se concatenaron en orden antes de comparar contra `text.txt`. En `batches` cada caso es una única secuencia.

---

## 3. Hallazgos por caso

### Modo `batches`

**test1 — Hernia discal / Durogesic / fentanilo.** ASR casi perfecto ("eficiencia" por "eficacia", no crítico). NER trunca "hernia" perdiendo "discal" → SNOMED 52515009 (hernia abdominal) **ERROR** de localización; pierde la dosis 50 μg/h. LLM **alucina** "50 mg/hora" (factor x1000); en la Impresión Diagnóstica usa el *fallback* "Cefalea a estudio" previsto en el `system_prompt` para diagnósticos ambiguos, justificado aquí porque solo recibe la entidad truncada "hernia" y no "hernia discal". FHIR estructuralmente correcto pero hereda el error de hernia.

**test2 — Sospecha de enfermedad celíaca.** ASR confunde "TTG" con "CTG" (cardiotocograma) y "amigdalitis"→"amitalitis". NER pierde la negación "no fumador"→"fumador". SNOMED mapea "atrofia moderada" a Charcot-Marie-Tooth y "CTG"→Mantoux positivo, ambos **ERROR grave**. El LLM **invierte el resultado genético** DQ2/DQ8 y omite la dieta sin gluten.

**test3 — Endometriosis de colon.** ASR fiel salvo pérdida de lateralidad "FII"→"FI". SNOMED con 5 errores graves: "HTA"→cefalea por hipertensión, "profunda"→tiña, "analítica"→balanza analítica, "estenosante"→colangitis esclerosante, "sigma"→letra griega. El informe LLM **niega falsamente** que hubiera tratamiento, cuando el FHIR documenta resección y anastomosis.

**test4 — Pancolitis ulcerosa / citoaféresis.** ASR deforma "micofenolato-mofetil" y "citoaféresis" sin recuperación. NER invierte polaridad ("sin complicaciones" tratado como complicación). SNOMED: "sangre roja"→hallazgo de orina. Informe invierte estado del tratamiento (azatioprina activa cuando está suspendida).

**test5 — Albinismo ocular / nistagmo / glioma.** ASR convierte "20/400" en "20 diagonal 400". NER no detecta ninguno de los dos diagnósticos (AOC, DG), solo la entidad genérica "agudeza visual". SNOMED mapea "amarillento"→especie de loro (Brotogeris tirica). LLM recurre al *fallback* "Cefalea a estudio" por falta de una entidad de diagnóstico concreta y, además, expande las siglas AOC/DG con desarrollos inventados ("Aparato Ocular Congénito", "Degeneración").

**test6 — Hematoma cerebeloso tras DLE.** ASR pierde la sigla "DLE"→"hundle"/"ley" en las 3 menciones. SNOMED: "superiores"→piezas dentales maxilares, "alta"→talla alta. NER solo entrega la entidad genérica "hipertensión" como diagnóstico, no "HCA"/hematoma cerebeloso. Informe reproduce literalmente "hundle" y, por la entidad de diagnóstico degradada, recurre al *fallback* "Cefalea a estudio" (aunque añade además, de forma incoherente, "Hematoma cerebral (presuntivo)").

**test7 — Papiloma invertido de uretra.** ASR muy fiel (~96-97%). NER pierde "disuria" y mapea "fosas lumbares"→fosas nasales. SNOMED: "defecto"→discapacidad, "anestesia"→hipoestesia cutánea, "uretra anterior"→atresia congénita. Informe es de los más fieles pero no señala estos errores de normalización.

**test8 — Gastrectomía Billroth II / sospecha neoplásica.** ASR deforma "Billroth II"→"Bilrod 2". NER pierde el hallazgo clínico central (infiltración neoplásica). SNOMED: "distendida"→vejiga urinaria distendida, "leve aumento"→síndrome de Potocki-Shaffer. El informe **alucina una mención a "CIE-9"** inexistente y omite la sospecha oncológica.

**test9 — SDRC pediátrico (recalculado).** El `Reporte.txt` original contenía un fragmento de audio ajeno al caso, cargado por error durante la evaluación, con 5 fármacos inexistentes (Enalapril, Losartán, Omeprazol, Metformina, Atorvastatina). No es una alucinación del ASR sino un error de carga del evaluador; descontado ese fragmento, el ASR transcribe correctamente el resto salvo "SDRC"→"DSDRC". El LLM **alucina "DSDRC (Distrofia de Duchenne de Becker)"**, confundiendo un síndrome de dolor regional complejo con una miopatía genética, a partir de ese error de transcripción real. El NER mantiene la pérdida de la negación sobre "traumatismo" ("sin traumatismo previo" tratado como hallazgo positivo).

**test10 — Neurofibromatosis tipo 1 / glioma del nervio óptico.** Mejor ASR de la serie (~99%). NER pierde la aparición real de proptosis en el seguimiento (solo registra la mención negada inicial). SNOMED: "corrección"→"Penal institution", "nuclear"→cromatina nuclear, "neuroimagen"→leucodistrofia rarísima. Informe limpio pero omite la evolución temporal.

### Modo `streaming`

**test1** — ASR casi perfecto (duplicación "Durogesic Durogesic"). NER etiqueta "analgesia" como PROBLEM (FP), pero sí identifica correctamente "hernia discal" (mencionada incluso en el Motivo de Consulta del propio informe). SNOMED: "doloroso"→31681005 "Trigeminal neuralgia" (CIE-10 G50.0 erróneo). El informe repite el error de dosis x1000 ("50 mg/hora") y, a pesar de tener "hernia discal" correctamente identificada, no la traslada a la Impresión Diagnóstica y usa el *fallback* "Cefalea a estudio" — a diferencia de `batches/test1`, aquí es un fallo real de abstracción del LLM, no de información de entrada.

**test2** — ASR: "TTG positiva"→"CTG positiva" (no corregido downstream). SNOMED catastrófico: "atrofia moderada"→Charcot-Marie-Tooth type 2B5; "positiva"→Mantoux positive. Informe omite el dato diagnóstico clave por el error ASR previo.

**test3** — ASR fusiona palabras ("tenesmorrectal", "hecesacintadas"). SNOMED: "la exploración"→"Exploration of cornea", "el estudio histológico"→"Atrichia with papular lesions". Informe colapsa formato y distorsiona la secuencia temporal del estudio histológico.

**test4** — NER no detecta negación: "no se presentaron complicaciones ni reacciones adversas" etiquetado como hallazgo positivo. SNOMED: "sangre, afectación"→"Acute undifferentiated leukemia". Informe invierte el sentido de la negación.

**test5** — NER nunca reconoce AOC/DG. SNOMED: "amarillento"→"Brotogeris tirica" (un loro), "corrección"→"Penal institution", "sin nevos" invierte la negación. Informe **alucina** expansiones de siglas inventadas.

**test6** — ASR pierde "DLE" dos veces de forma distinta. SNOMED: "ley"→"Leyte" (isla de Filipinas). Informe es una **alucinación masiva**: describe "insuficiencia cardíaca" ajena por completo al caso real. Tiempo anómalo (412.8s).

**test7** — Duplicados de streaming en "disuria"/"uretrorragia". SNOMED invierte semántica: "cardiorespiratoria"→"Cardiorespiratory failure" cuando la auscultación es normal. FHIR con Condition duplicados.

**test8** — ASR pierde "Billroth II"→"Bilrod 2". SNOMED grave y peligroso: "intervenido"→"Believes phones are bugged" (trastorno delirante, F22.0) en cirugía digestiva. Informe alucina equivalencia falsa (Q63.8 ≈ Hirschsprung).

**test9** — Mejor caso del conjunto. SNOMED mayormente coherente, salvo negación de "traumatismo" no detectada. Repite el patrón "Cefalea a estudio" aunque se autocorrige luego en el propio texto.

**test10** — ASR pierde "proptosis"→"proctosis". SNOMED: "una resonancia magnética nuclear"→síndrome genético raro; "corrección"→"Penal institution" (mismo error que test5). Informe alucina conceptos SNOMED inexistentes en Reporte.txt. Tiempo total más alto (378.2s).

---

## 4. Hallazgos transversales (ambos modos)

- **Desambiguación SNOMED sin contexto de frase** es el fallo más grave y sistemático del pipeline en los dos modos. El motor de enlace opera por coincidencia léxica superficial sobre calificadores/palabras sueltas en lugar de la frase clínica completa, produciendo mapeos absurdos y a veces peligrosos: "corrección"→"Penal institution" (repetido idéntico en `batches/test10`, `streaming/test5` y `streaming/test10` — indica un fallo determinístico del diccionario de enlace, no ruido aleatorio), "intervenido"→trastorno delirante, "amarillento"→especie de loro, "atrofia moderada"→Charcot-Marie-Tooth.
- **Pérdida sistemática de negaciones y polaridad clínica**: "no fumador"→fumador, "sin complicaciones"→complicación activa, "sin traumatismo"→traumatismo activo. Se repite en ambos modos y se propaga sin filtro hasta `clinicalStatus: active` en FHIR — el riesgo clínico más recurrente de todo el sistema.
- **"Cefalea a estudio" no es una alucinación de plantilla, sino un *fallback* explícito del `system_prompt`** (`backend/asr-service/config.yaml`: *"Si es ambiguo, pon 'Cefalea a estudio' o similar"*), activado en 5 de los 20 informes evaluados (batches/test1, test5, test6; streaming/test1, test9). En la mayoría de estos casos (batches/test1, test5, test6; streaming/test9) la causa raíz es que el NER solo entrega al LLM una entidad de diagnóstico genérica o truncada, dejándolo sin la información necesaria; en streaming/test1, en cambio, el NER sí entrega "hernia discal" correctamente (el propio informe la menciona en el Motivo de Consulta) y el LLM aun así no la traslada a la Impresión Diagnóstica, lo que evidencia una limitación real de abstracción del modelo. Recomendación de diseño: el *prompt* no debería sugerir un término clínico concreto y ajeno al caso como valor de contingencia, sino indicar la ausencia de información suficiente.
- **Siglas y epónimos clínicos son el punto más frágil del ASR**: TTG, DLE, FII, Billroth II, AOC/DG se transcriben mal de forma persistente en ambos modos y casi nunca se recuperan en etapas posteriores, mientras que errores ortográficos menores sí se diluyen sin impacto downstream.
- **Alucinaciones del LLM frecuentes y de gravedad variable**: invención de diagnósticos, inversión de datos críticos (DQ2/DQ8, estado de tratamiento), expansión incorrecta de siglas (DSDRC→Duchenne de Becker), referencia a sistemas inexistentes (CIE-9), error de magnitud de dosis (50 μg→50 mg). Tasa de alucinación relevante: 70% en `batches`, 80% en `streaming`.
- **FHIR es la etapa estructuralmente más sólida pero acrítica**: siempre bien formado (resourceType, subject, meta.profile correctos), pero actúa como amplificador de confianza, persistiendo con apariencia de dato clínico fiable errores de polaridad y desambiguación que en NER/SNOMED eran señales de baja confianza.
- **Cobertura CIE-10 muy baja en ambos modos** (~10-20% batches, algo mejor en streaming pero aún deficitaria), limitando la interoperabilidad real del Bundle.
- **`streaming` mejora ASR y NER frente a `batches`** (medias 4.0 vs 3.75 y 2.9 vs 2.10) probablemente por mayor ventana de contexto/reintento entre secuencias, pero **multiplica el tiempo total ~6x** (184.9 s vs 30.6 s de media) sin mejorar de forma significativa la terminología (1.9 vs 1.55) ni eliminar las alucinaciones del LLM, que de hecho son ligeramente más frecuentes en streaming.
- **Nota de calidad de datos**: el caso `batches/test9` se recalculó tras detectar que el archivo de evaluación original contenía un fragmento de audio ajeno al caso (error de carga del evaluador, no del sistema) con 5 fármacos inexistentes. El hallazgo de riesgo de seguridad del paciente asociado a ese fragmento queda invalidado; los errores reales y representativos del caso (transcripción "SDRC"→"DSDRC", expansión incorrecta del LLM a "Duchenne de Becker", pérdida de negación en "traumatismo") ya están recogidos en los puntos anteriores.

---

## 5. Métricas agregadas

| Métrica | Batches | Streaming |
|---|---|---|
| WER medio (ASR) | ~6-8% | ~5-10% |
| Precisión NER (aprox.) | ~50% | ~65-75% |
| Recall NER (aprox.) | ~48% | ~60-70% |
| % entidades sin mapeo SNOMED | ~15-20% | ~25-50% (rango amplio) |
| % entidades sin código CIE-10 | ~80-90% | mayoritario, algo mejor que batches |
| % casos con alucinación relevante en Informe LLM | 70% (7/10) | 80% (8/10) |
| Tiempo medio total por caso | ~30.6 s | ~184.9 s |
| Etapa dominante en tiempo | ASR (~70-85%) | NER+ConceptMap (>80% en casos grandes) |

---

## 6. Recomendaciones priorizadas

1. **Reescribir el enlace terminológico SNOMED para usar contexto de frase, no palabras/calificadores aislados.** Es el fallo más grave, más frecuente y con mayor riesgo clínico (codifica intervenciones quirúrgicas como trastornos psiquiátricos, anatomía como especies de animales o ubicaciones geográficas). Tiene mayor impacto que cualquier otra mejora porque contamina Informe.txt y FHIR aguas abajo.
2. **Implementar detección y propagación de negación** en NER (y verificarla antes de fijar `clinicalStatus` en FHIR). Es el segundo patrón más repetido y el de mayor riesgo de seguridad del paciente al invertir hallazgos clínicos.
3. **Añadir guardrails anti-alucinación al prompt del LLM generador** (p. ej. obligar a citar solo entidades/códigos presentes en el Reporte.txt, validar magnitudes de dosis contra el texto fuente) y **rediseñar el *fallback* de la Impresión Diagnóstica**: en lugar de sugerir un término concreto ajeno al caso ("Cefalea a estudio"), indicar la ausencia de información suficiente e instruir al modelo a intentar sintetizar el diagnóstico a partir de las entidades ya presentes en el resto del informe (Motivo de Consulta, anexo SNOMED) antes de recurrir a él.
4. **Reforzar el ASR para siglas y epónimos clínicos** (diccionario médico específico o re-puntuación con n-gramas clínicos) — DLE, TTG, Billroth II, AOC/DG fallan de forma sistemática y rara vez se recuperan después.
5. **Mejorar cobertura de ConceptMap CIE-10**, hoy el cuello de botella de interoperabilidad (80-90% sin código en batches).
6. **Investigar el escalado de tiempo no lineal en streaming** (NER+ConceptMap consumen >80% del tiempo en casos grandes como test6/test10) antes de adoptarlo en producción, dado que la mejora en ASR/NER no compensa claramente el coste de tiempo de ~6x frente a batches.
