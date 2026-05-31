"""Zielgruppen-Mapping für Schlüsselkompetenzen.

Eine Zielgruppe (Angebotsstil) bestimmt:
- die Benennung der vier Kompetenz-Kategorien (LABEL_MAP)
- die Prominenz-Reihenfolge in der Ausgabe (PROMINENZ)

Wird von src/pim_to_psm.py konsumiert. Keine Abhängigkeit auf andere src/-Module
— pure Datenstruktur + Lookup-Funktionen.

Phase 8b G3 Migration (2026-05-31): `technologie` und `spezialgebiet` raus —
ersetzt durch eigenständige `Wissensgebiet`-Sektion (IT-Know-How).
"""

from __future__ import annotations

KATEGORIEN: tuple[str, ...] = (
    "methodenkompetenz",
    "fachkompetenz",
    "fuehrungkompetenz",
    "programmierparadigmen",
)

LABEL_MAP: dict[str, dict[str, str]] = {
    "Behoerde": {
        "methodenkompetenz": "Methoden- & Prozesskompetenz",
        "fachkompetenz": "Fachkompetenz",
        "fuehrungkompetenz": "Führungs- & Leitungskompetenz",
        "programmierparadigmen": "Programmier-Paradigmen",
    },
    "Consultant": {
        "methodenkompetenz": "Beratungsansatz & Methodik",
        "fachkompetenz": "Branchenexpertise",
        "fuehrungkompetenz": "Stakeholder-Management",
        "programmierparadigmen": "Programmier-Paradigmen",
    },
    "StartUp": {
        "methodenkompetenz": "Agile / DevOps",
        "fachkompetenz": "Domänenwissen",
        "fuehrungkompetenz": "Leadership",
        "programmierparadigmen": "Programmier-Paradigmen",
    },
    "Wissenschaftlich": {
        "methodenkompetenz": "Forschungsmethodik",
        "fachkompetenz": "Fachgebiet",
        "fuehrungkompetenz": "Kooperation & Betreuung",
        "programmierparadigmen": "Programmier-Paradigmen",
    },
    "Standard": {
        "methodenkompetenz": "Methodenkompetenz",
        "fachkompetenz": "Fachkompetenz",
        "fuehrungkompetenz": "Führungskompetenz",
        "programmierparadigmen": "Programmier-Paradigmen",
    },
    "AIGovernance": {
        "methodenkompetenz": "Governance-Frameworks & Risk Management",
        "fachkompetenz": "AI Act, DORA, ISO 42001, NIST AI RMF",
        "fuehrungkompetenz": "AI-Oversight & Board-Advisory",
        "programmierparadigmen": "Programmier-Paradigmen",
    },
}

# Prominenz: Reihenfolge in der die Kategorien je Stil dargestellt werden.
# „programmierparadigmen" rangiert in allen Stilen am Ende (Senior-relevant,
# aber kein primärer Verkaufsanker).
PROMINENZ: dict[str, list[str]] = {
    "Behoerde": [
        "fachkompetenz",
        "methodenkompetenz",
        "fuehrungkompetenz",
        "programmierparadigmen",
    ],
    "Consultant": [
        "methodenkompetenz",
        "fachkompetenz",
        "fuehrungkompetenz",
        "programmierparadigmen",
    ],
    "StartUp": [
        "methodenkompetenz",
        "fachkompetenz",
        "fuehrungkompetenz",
        "programmierparadigmen",
    ],
    "Wissenschaftlich": [
        "methodenkompetenz",
        "fachkompetenz",
        "fuehrungkompetenz",
        "programmierparadigmen",
    ],
    "Standard": [
        "methodenkompetenz",
        "fachkompetenz",
        "fuehrungkompetenz",
        "programmierparadigmen",
    ],
    "AIGovernance": [
        "fachkompetenz",
        "methodenkompetenz",
        "fuehrungkompetenz",
        "programmierparadigmen",
    ],
}

DEFAULT_STIL = "Standard"


def resolve_stil(zielgruppe: str | None) -> str:
    """Gibt einen gültigen Stil-Schlüssel zurück, sonst DEFAULT_STIL."""
    if zielgruppe and zielgruppe in LABEL_MAP:
        return zielgruppe
    return DEFAULT_STIL


def kategorien_fuer_zielgruppe(zielgruppe: str | None) -> list[tuple[str, str]]:
    """Gibt [(kategorie_key, label), ...] in Prominenz-Reihenfolge."""
    stil = resolve_stil(zielgruppe)
    return [(key, LABEL_MAP[stil][key]) for key in PROMINENZ[stil]]
