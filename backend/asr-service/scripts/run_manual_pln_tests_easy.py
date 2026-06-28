"""Variant of run_manual_pln_tests.py with looser ("easier") expected_entities.

Reuses the same 10 gold-standard texts, but instead of expecting full
semantic phrases (e.g. "atrofia moderada de las vellosidades intestinales"),
expects the shorter fragments the model tends to actually produce
(e.g. "atrofia moderada", "vellosidades intestinales"). This isolates how
much of the low F1 in the strict test is due to span granularity rather than
missed clinical content.

Usage:
    .venv/bin/python scripts/run_manual_pln_tests_easy.py [--base-url http://localhost:8001]
"""

import argparse
from pathlib import Path

from run_manual_pln_tests import TEST_CASES, run

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports" / "manual_reports_easy"

EASY_EXPECTED_ENTITIES: dict[int, list[str]] = {
    1: ["hernia discal", "Durogesic", "50 μg/h", "fentanilo", "cuadro doloroso", "analgesia"],
    2: ["Amigdalitis", "repetición", "transaminasas", "TTG", "DQ2", "DQ8", "biopsia duodenal", "atrofia moderada", "vellosidades intestinales", "infiltrado inflamatorio", "DSG"],
    3: ["hernia umbilical", "HTA", "dolor", "FII", "tenesmo rectal", "heces acintadas", "16.000 leucocitos", "91% neutrofilos", "enema opaco", "colonoscopia", "imagen estenosante", "resección", "zona estenosante", "anastomosis", "término-terminal", "endometriosis", "colon", "fibrosis", "hemorragia"],
    4: ["pancolitis ulcerosa", "diarrea", "pérdida de peso", "15 kg", "azatioprina", "colitis ulcerosa", "cortirrefractariedad", "citoaféresis", "micofenolato-mofetil"],
    5: ["agudeza visual", "exotropía", "50 dioptrías", "nistagmo horizontal", "presión intraocular", "12 mmHg", "hipoplasia foveal", "AOC", "DG"],
    6: ["hipertensión arterial", "ataxia", "marcha", "incontinencia", "esfínteres", "trastorno", "funciones superiores", "neuroimagen", "HCA", "DLE", "cefaleas", "vómitos", "510 ml", "LCR", "TC craneal", "hematoma", "hemisferio cerebeloso izquierdo", "RM cerebral"],
    7: ["disuria", "uretrorragia", "ecografía urológica", "cistouretroscopía", "radiografía", "uretrocistografía miccional", "estudio endoscópico", "resección endoscópica", "papiloma invertido", "uretra anterior"],
    8: ["gastrectomía parcial", "ulcus gástrico", "péptico", "Billroth II", "dolor abdominal", "amilasa", "550 unidades interlacionales", "lipasa", "5976 unidades interlacionales", "ecografía abdominal", "dilatación", "vías biliares", "TAC", "RMN", "endoscopia digestiva alta", "infiltración neoplásica", "gastrectomía total", "anastomosis", "esófago-yeyunal"],
    9: ["SDRC", "capsaicina", "8 %"],
    10: ["neurofibromatosis", "tipo 1", "resonancia magnética nuclear", "exploración biomicroscópica", "funduscopia", "neuroimagen", "glioma", "nervio óptico", "proptosis"],
}


def build_easy_test_cases() -> dict[int, dict]:
    return {
        test_id: {"text": case["text"], "expected_entities": EASY_EXPECTED_ENTITIES[test_id]}
        for test_id, case in TEST_CASES.items()
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8001", help="URL base del asr-service")
    args = parser.parse_args()
    run(args.base_url, test_cases=build_easy_test_cases(), reports_dir=REPORTS_DIR)
