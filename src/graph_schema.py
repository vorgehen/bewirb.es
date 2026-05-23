# AUTO-GENERATED -- nicht manuell bearbeiten.
# Quelle: grammar/profile.tx  ->  codegen/codegen.py

NODE_TYPES: list[str] = [
    "Person",
    "Kontakt",
    "Technologiekompetenz",
    "Branche",
    "Auftraggeber",
    "Projekterfahrung",
    "Ausbildung",
]

PERSON_ATTRS: list[str] = [
    "name",
    "title",
    "contact",
]
KONTAKT_ATTRS: list[str] = [
    "email",
    "phone",
    "location",
    "website",
    "linkedin",
    "github",
]
TECHNOLOGIEKOMPETENZ_ATTRS: list[str] = [
    "name",
    "category",
    "proficiency",
    "years",
    "keywords",
]
BRANCHE_ATTRS: list[str] = [
    "name",
    "label",
]
AUFTRAGGEBER_ATTRS: list[str] = [
    "name",
    "label",
    "location",
]
PROJEKTERFAHRUNG_ATTRS: list[str] = [
    "name",
    "title",
    "auftraggeber",
    "branche",
    "start",
    "end",
    "rolle",
    "uses",
    "keywords",
    "description",
    "achievements",
]
AUSBILDUNG_ATTRS: list[str] = [
    "name",
    "title",
    "institution",
    "start",
    "end",
    "abschluss",
]
