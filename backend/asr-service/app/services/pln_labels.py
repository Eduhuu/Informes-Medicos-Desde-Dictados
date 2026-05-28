from app.constants.messages import (
    REPORT_PLN_SOURCE_FARMACOS,
    REPORT_PLN_SOURCE_MEDICAL,
    REPORT_PLN_SOURCE_UNKNOWN,
)
from shared.constants.PlnConstants import (
    PLN_SOURCE_FARMACOS,
    PLN_SOURCE_MEDICAL,
)

_PLN_SOURCE_LABELS = {
    PLN_SOURCE_MEDICAL: REPORT_PLN_SOURCE_MEDICAL,
    PLN_SOURCE_FARMACOS: REPORT_PLN_SOURCE_FARMACOS,
}


def pln_source_label(pln_source: str) -> str:
    """Map internal PLN source id to a Spanish display label."""
    return _PLN_SOURCE_LABELS.get(pln_source, REPORT_PLN_SOURCE_UNKNOWN)
