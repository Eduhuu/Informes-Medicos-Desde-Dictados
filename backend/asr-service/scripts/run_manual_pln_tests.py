"""Run the 10 manual NER evaluation cases against POST /pln-test.

Sends each case (gold standard text + expected_entities) to the running
asr-service, stores the raw response under reports/manual_reports/test<N>/
pln_test.json and writes an averaged resumen.json at reports/manual_reports/.

Usage:
    .venv/bin/python scripts/run_manual_pln_tests.py [--base-url http://localhost:8001]
"""

import argparse
import json
import statistics
from pathlib import Path

import requests

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports" / "manual_reports"

TEST_CASES: dict[int, dict] = {
    1: {
        "text": "Paciente mujer de 53 años de edad, diagnosticada de hernia discal, en tratamiento con Durogesic 50 μg/h durante 6 años, con buena eficacia y seguridad. Se cambia por fentanilo genérico, y se nota un empeoramiento del cuadro doloroso. Se vuelve a cambiar a Durogesic®, y de nuevo se estabiliza la analgesia.",
        "expected_entities": ["hernia discal", "Durogesic", "50 μg/h", "fentanilo", "cuadro doloroso", "analgesia"],
    },
    2: {
        "text": "Varón de 29 años. Hijo mediano de tres hermanos (los otros dos, están sanos). Casado y sin hijos. No bebedor, ni fumador. Amigdalitis de repetición en la infancia, siendo operado a los 6 años. Asintomático. Hábito intestinal normal. Analítica normal con ligera elevación persistente en las transaminasas. TTG positiva (2,46). DQ2 (-) y DQ8 (+). La biopsia duodenal mostró atrofia moderada de las vellosidades intestinales, acompañada de infiltrado inflamatorio importante, a nivel de la lámina propia. Está con DSG desde hace 2 años, con buena respuesta clínica y analítica.",
        "expected_entities": ["Amigdalitis de repetición", "transaminasas", "TTG", "DQ2", "DQ8", "biopsia duodenal", "atrofia moderada de las vellosidades intestinales", "infiltrado inflamatorio", "DSG"],
    },
    3: {
        "text": "Mujer de 42 años de edad con antecedentes personales de hernia umbilical intervenida, HTA. Presentaba dolor en FII de 2 años de evolución, tenesmo rectal y heces acintadas. A la exploración física destacaba dolor difuso a la palpación profunda en FII. En la analítica destacaba 16.000 leucocitos y 91% neutrofilos. Se realizó enema opaco y colonoscopia en ambas destacaba una imagen estenosante a nivel de sigma. El estudio histológico de las biopsias no fue concluyente. Se realizó la resección de la zona estenosante con anastomosis término-terminal. El estudio histológico infirmó la lesión de endometriosis de colon con afectación transmural ocasionando áreas de fibrosis y de hemorragia.",
        "expected_entities": ["hernia umbilical", "HTA", "dolor en FII", "tenesmo rectal", "heces acintadas", "16.000 leucocitos", "91% neutrofilos", "enema opaco", "colonoscopia", "imagen estenosante", "resección de la zona estenosante", "anastomosis término-terminal", "endometriosis de colon", "fibrosis", "hemorragia"],
    },
    4: {
        "text": "Paciente de 38 años diagnosticado de pancolitis ulcerosa desde el año 2004, corticodependiente. Ese mismo año presenta un cuadro de actividad inflamatoria intestinal con diarrea sin sangre, afectación importante del estado general y pérdida de peso de 15 kg en un mes, así como intolerancia digestiva a tratamiento con azatioprina. Durante estos 3 últimos años ha precisado varios ingresos debidos a graves brotes de diarrea (5-6 deposiciones diarias) con sangre roja.\nEn junio de 2007 presentó un brote prolongado de colitis ulcerosa con activación moderada y mala respuesta al tratamiento farmacológico con criterios de cortirrefractariedad, momento en el que se inicia la citoaféresis, recibiendo una sesión cada 7 días durante 5 semanas. Las vías de acceso fueron las venas antecubitales de los brazos, y durante las sesiones no se presentaron complicaciones ni reacciones adversas. Desde la segunda sesión presentó una notable mejoría clínica y en la actualidad recibe tratamiento oral de micofenolato-mofetil.",
        "expected_entities": ["pancolitis ulcerosa", "diarrea", "pérdida de peso de 15 kg", "azatioprina", "colitis ulcerosa", "cortirrefractariedad", "citoaféresis", "micofenolato-mofetil"],
    },
    5: {
        "text": "Mujer de 35 años acude a consulta por mala agudeza visual desde la infancia, sin tratamiento. A la exploración se encontró cabello amarillento, al igual que cejas y pestañas; piel rojiza, sin nevos ; agudeza visual con corrección de 20/400 en ojo derecho 20/200 en ojo izquierdo; exotropía de 50 dioptrías, nistagmo horizontal; ambos ojos con presión intraocular de 12 mmHg, conjuntiva normal, córnea con algunos depósitos estromales blanquecinos centrales y anteriores bien circunscritos, cámara anterior sin células ni flare, iris claro con transiluminación, cristalino transparente e hipoplasia foveal. Con los datos clínicos oculares y sistémicos se establecieron los diagnósticos de AOC y DG y se citó a la familia para valoración clínica.\n\nSe trata de una familia de nueve miembros, con padres de 74 y 64 años. No hay consanguinidad y proceden de localidades diferentes. La DG está presente en la madre, tres hermanos y su hijo, mientras que el AOC aparece en dos de los hermanos pero sin datos de DG.",
        "expected_entities": ["mala agudeza visual", "exotropía de 50 dioptrías", "nistagmo horizontal", "presión intraocular de 12 mmHg", "hipoplasia foveal", "AOC", "DG"],
    },
    6: {
        "text": "Mujer de 77 años de edad con único antecedente de hipertensión arterial. Presentaba un cuadro clínico consistente en ataxia de la marcha, incontinencia de esfínteres y trastorno de funciones superiores. Los estudios de neuroimagen mostraron dilatación del sistema ventricular, por lo que, ante la sospecha de una HCA, se procedió a la colocación de un DLE. A las 30 horas de su colocación comenzó, bruscamente, a presentar cefaleas y vómitos no asociados a ortostatismo. No hubo deterioro del nivel de consciencia. En la bolsa de drenaje había 510 ml de LCR. Una TC craneal, mostró un hematoma en el hemisferio cerebeloso izquierdo, de disposición transversal, con escaso efecto de masa. Ante los hallazgos y la situación clínica de la paciente, se decidió la retirada del DLE y tratamiento conservador. En la RM cerebral realizada previa al ingreso se había descartado patología subyacente. A los cinco días la paciente fue dada de alta con recuperación hasta su estado premórbido.\nNo se le implantó válvula de derivación al no objetivarse mejoría con la colocación de DLE.",
        "expected_entities": ["hipertensión arterial", "ataxia de la marcha", "incontinencia de esfínteres", "trastorno de funciones superiores", "neuroimagen", "HCA", "DLE", "cefaleas", "vómitos", "510 ml de LCR", "TC craneal", "hematoma en el hemisferio cerebeloso izquierdo", "RM cerebral"],
    },
    7: {
        "text": "Paciente varón, de 40 años de edad, con antecedentes de salud. Acude a consulta de Urología por presentar disuria y 3 episodios de uretrorragia. Al examen físico las mucosas son húmedas y normocoloreadas, la auscultación cardio-respiratoria es normal, el abdomen es negativo, fosas lumbares libres, el tacto rectal, los genitales externos y las regiones inguinales son normales. Se le realiza ecografía urológica que es normal. La cistouretroscopía es normal, sólo notándose un leve resalto al paso del cistoscopio por uretra anterior. Se le realiza radiografía de uretrocistografía miccional donde se observa un defecto de llenado a nivel de la uretra anterior.\n\nPor todo lo anterior decidimos realizar un estudio endoscópico bajo anestesia, detectándose una tumoración polipoide, de color rojiza, bien delimitada, por lo que se decide resección endoscópica de la misma. El resultado anatomopatológico de la pieza quirúrgica fue un papiloma invertido de uretra anterior. Se da de alta por mejoría, evolucionando satisfactoriamente con desaparición de la disuria y la uretrorragia.",
        "expected_entities": ["disuria", "uretrorragia", "ecografía urológica", "cistouretroscopía", "radiografía de uretrocistografía miccional", "estudio endoscópico", "resección endoscópica", "papiloma invertido de uretra anterior"],
    },
    8: {
        "text": "Paciente varón de 69 años, con antecedente de gastrectomía parcial hace 30 años por ulcus gástrico péptico con reconstrucción de tipo Billroth II que ingresa por clínica de ocho días de evolución consistente en dolor abdominal localizado en mesogastrio junto a un leve aumento de las cifras de amilasa y lipasa séricas (amilasa 550 unidades interlacionales por litro, lipasa 5976 unidades interlacionales por litro). La ecografía abdominal mostró la vesícula biliar distendida junto a una dilatación de las vías biliares intra y extrahepáticas y una gran formación quística de paredes finas y morfología tubular ocupando desde hipocondrio izquierdo hasta vacío derecho, lo que sugería que se tratase del asa aferente dilatada y replecionada de líquido. La TAC y la RMN confirmaron estos hallazgos. La endoscopia digestiva alta permitió visualizar la existencia de pliegues engrosados en el muñón gástrico que obstruían el asa aferente, lo que sugería infiltración neoplásica que fue confirmada tras el estudio histológico de las biopsias endoscópicas. El paciente fue intervenido quirúrgicamente, con gastrectomía total y anastomosis esófago-yeyunal.",
        "expected_entities": ["gastrectomía parcial", "ulcus gástrico péptico", "Billroth II", "dolor abdominal", "amilasa 550 unidades interlacionales por litro", "lipasa 5976 unidades interlacionales por litro", "ecografía abdominal", "dilatación de las vías biliares", "TAC", "RMN", "endoscopia digestiva alta", "infiltración neoplásica", "gastrectomía total", "anastomosis esófago-yeyunal"],
    },
    9: {
        "text": "Niña de 13 años de edad cuando se realiza el diagnóstico de SDRC en ambas extremidades inferiores sin traumatismo previo.\nDerivada a la Unidad del Dolor por el Servicio de Traumatología Pediátrica a los cuatro meses del diagnóstico. Se administró tratamiento farmacológico más aplicación del parche de capsaicina al 8 % con remisión completa del cuadro.",
        "expected_entities": ["SDRC", "capsaicina al 8 %"],
    },
    10: {
        "text": "Niña de tres años de edad diagnosticada hace un año de neurofibromatosis tipo 1 por el servicio de pediatría. Se remite a oftalmología para valoración, en el contexto del cribado de otras patologías que se lleva a cabo en estos pacientes. Por ello, también se solicita una resonancia magnética nuclear (RMN) craneal.\nEn este momento la paciente carecía de sintomatología alguna y la exploración era la siguiente: agudeza visual sin corrección en el ojo derecho 0,9 y en el izquierdo 1. Exploración biomicroscópica del segmento anterior era normal, así como la funduscopia en ambos ojos. Presión intraocular normal en los dos ojos. Movimientos oculares externos, sin hallazgos patológicos. No proptosis ni exoftalmos. Pupilas isocóricas y normorreactivas.\nEn el estudio con neuroimagen con RMN se detectó la presencia de un glioma del nervio óptico del ojo izquierdo.\nSe decidió no tratar, pero seguir a la paciente con revisiones periódicas, cada tres meses, por nuestra parte. En dicho seguimiento, progresivamente ha aparecido una leve proptosis y la visión de la paciente ha disminuido a 0,9 en el ojo izquierdo.",
        "expected_entities": ["neurofibromatosis tipo 1", "resonancia magnética nuclear", "exploración biomicroscópica", "funduscopia", "neuroimagen", "glioma del nervio óptico", "proptosis"],
    },
}


def run(base_url: str, test_cases: dict[int, dict] = TEST_CASES, reports_dir: Path = REPORTS_DIR) -> None:
    summaries = []
    for test_id, case in sorted(test_cases.items()):
        response = requests.post(f"{base_url}/pln-test", json=case, timeout=120)
        response.raise_for_status()
        result = response.json()

        test_dir = reports_dir / f"test{test_id}"
        test_dir.mkdir(parents=True, exist_ok=True)
        output_path = test_dir / "pln_test.json"
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        metrics = result.get("metrics") or {}
        print(f"Test{test_id}: P={metrics.get('precision')} R={metrics.get('recall')} F1={metrics.get('f1_score')}")
        summaries.append({"test": test_id, **metrics})

    write_summary(summaries, reports_dir)


def write_summary(summaries: list[dict], reports_dir: Path = REPORTS_DIR) -> None:
    with_metrics = [s for s in summaries if "precision" in s]

    tp_total = sum(s["true_positives"] for s in with_metrics)
    fp_total = sum(s["false_positives"] for s in with_metrics)
    fn_total = sum(s["false_negatives"] for s in with_metrics)
    micro_precision = tp_total / (tp_total + fp_total) if (tp_total + fp_total) else 0.0
    micro_recall = tp_total / (tp_total + fn_total) if (tp_total + fn_total) else 0.0
    micro_f1 = (
        2 * micro_precision * micro_recall / (micro_precision + micro_recall)
        if (micro_precision + micro_recall)
        else 0.0
    )

    summary = {
        "per_test": summaries,
        "macro_average": {
            "precision": round(statistics.mean(s["precision"] for s in with_metrics), 4),
            "recall": round(statistics.mean(s["recall"] for s in with_metrics), 4),
            "f1_score": round(statistics.mean(s["f1_score"] for s in with_metrics), 4),
        },
        "micro_average": {
            "precision": round(micro_precision, 4),
            "recall": round(micro_recall, 4),
            "f1_score": round(micro_f1, 4),
            "true_positives": tp_total,
            "false_positives": fp_total,
            "false_negatives": fn_total,
        },
    }

    summary_path = reports_dir / "resumen.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResumen guardado en {summary_path}")
    print(f"Macro F1={summary['macro_average']['f1_score']}  Micro F1={summary['micro_average']['f1_score']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8001", help="URL base del asr-service")
    args = parser.parse_args()
    run(args.base_url)
