"""Zielgruppen-Mapping für Schlüsselkompetenzen.

Eine Zielgruppe (Angebotsstil) bestimmt:
- die Benennung der fünf Kompetenz-Kategorien (LABEL_MAP)
- die Prominenz-Reihenfolge in der Ausgabe (PROMINENZ)

Wird von src/pim_to_psm.py konsumiert. Keine Abhängigkeit auf andere src/-Module
— pure Datenstruktur + Lookup-Funktionen.
"""

from __future__ import annotations

KATEGORIEN: tuple[str, ...] = (
    "methodenkompetenz",
    "fachkompetenz",
    "technologie",
    "spezialgebiet",
    "fuehrungkompetenz",
)

LABEL_MAP: dict[str, dict[str, str]] = {
    "Behoerde": {
        "methodenkompetenz": "Methoden- & Prozesskompetenz",
        "fachkompetenz": "Fachkompetenz",
        "technologie": "IT-Know-How",
        "spezialgebiet": "Besondere IT-Kenntnisse",
        "fuehrungkompetenz": "Führungs- & Leitungskompetenz",
    },
    "Consultant": {
        "methodenkompetenz": "Beratungsansatz & Methodik",
        "fachkompetenz": "Branchenexpertise",
        "technologie": "Technologiestack",
        "spezialgebiet": "Spezialgebiete",
        "fuehrungkompetenz": "Stakeholder-Management",
    },
    "StartUp": {
        "methodenkompetenz": "Agile / DevOps",
        "fachkompetenz": "Domänenwissen",
        "technologie": "Tech Stack",
        "spezialgebiet": "Spezialgebiete",
        "fuehrungkompetenz": "Leadership",
    },
    "Wissenschaftlich": {
        "methodenkompetenz": "Forschungsmethodik",
        "fachkompetenz": "Fachgebiet",
        "technologie": "Technologiebasis",
        "spezialgebiet": "Forschungsschwerpunkte",
        "fuehrungkompetenz": "Kooperation & Betreuung",
    },
    "Standard": {
        "methodenkompetenz": "Methodenkompetenz",
        "fachkompetenz": "Fachkompetenz",
        "technologie": "Technologiekompetenz",
        "spezialgebiet": "Spezielle IT-Kenntnisse",
        "fuehrungkompetenz": "Führungskompetenz",
    },
    "AIGovernance": {
        "methodenkompetenz": "Governance-Frameworks & Risk Management",
        "fachkompetenz": "AI Act, DORA, ISO 42001, NIST AI RMF",
        "technologie": "AI-Stack (governance-relevant)",
        "spezialgebiet": "Responsible AI Patterns",
        "fuehrungkompetenz": "AI-Oversight & Board-Advisory",
    },
}

# Prominenz: Reihenfolge in der die Kategorien je Stil dargestellt werden.
PROMINENZ: dict[str, list[str]] = {
    "Behoerde": [
        "fachkompetenz",
        "methodenkompetenz",
        "fuehrungkompetenz",
        "technologie",
        "spezialgebiet",
    ],
    "Consultant": [
        "methodenkompetenz",
        "fachkompetenz",
        "fuehrungkompetenz",
        "technologie",
        "spezialgebiet",
    ],
    "StartUp": [
        "technologie",
        "methodenkompetenz",
        "spezialgebiet",
        "fuehrungkompetenz",
        "fachkompetenz",
    ],
    "Wissenschaftlich": [
        "methodenkompetenz",
        "spezialgebiet",
        "fachkompetenz",
        "technologie",
        "fuehrungkompetenz",
    ],
    "Standard": [
        "methodenkompetenz",
        "fachkompetenz",
        "technologie",
        "spezialgebiet",
        "fuehrungkompetenz",
    ],
    "AIGovernance": [
        "fachkompetenz",
        "methodenkompetenz",
        "fuehrungkompetenz",
        "spezialgebiet",
        "technologie",
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
