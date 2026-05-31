# AUTO-GENERATED -- nicht manuell bearbeiten.
# Quelle: grammar/{profile.tx, knowledge.tx}  ->  codegen/codegen.py

NODE_TYPES: list[str] = [
    "Person",
    "PersoenlicheDaten",
    "Kontakt",
    "Branche",
    "Auftraggeber",
    "Projekterfahrung",
    "Ausbildung",
    "Sprache",
    "Zertifikat",
    "Werdegang",
    "Schluesselkompetenzen",
    "WissenschaftlichesInteresse",
    "Wissensgebiet",
    "Subkategorie",
    "Technology",
    "SfiaLevel",
    "TechnologyRelation",
    "RoleProfile",
    "CompetencyArea",
    "Preference",
    "WarnRule",
    "BoostRule",
    "DeprioritizeRule",
]

PERSON_ATTRS: list[str] = [
    "name",
    "title",
    "contact",
    "kurzprofil",
    "persoenlicheDaten",
]
PERSOENLICHEDATEN_ATTRS: list[str] = [
    "geburtsdatum",
    "geburtsort",
    "staatsangehoerigkeit",
    "familienstand",
    "kinder",
]
KONTAKT_ATTRS: list[str] = [
    "email",
    "phone",
    "festnetz",
    "location",
    "website",
    "linkedin",
    "github",
]
BRANCHE_ATTRS: list[str] = [
    "name",
    "label",
]
AUFTRAGGEBER_ATTRS: list[str] = [
    "name",
    "label",
    "location",
    "extern",
    "interna",
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
SPRACHE_ATTRS: list[str] = [
    "name",
    "bezeichnung",
    "level",
]
ZERTIFIKAT_ATTRS: list[str] = [
    "name",
    "titel",
    "aussteller",
    "jahr",
    "url",
]
WERDEGANG_ATTRS: list[str] = [
    "name",
    "titel",
    "arbeitgeber",
    "start",
    "end",
    "beschreibung",
]
SCHLUESSELKOMPETENZEN_ATTRS: list[str] = [
    "methodenkompetenz",
    "fachkompetenz",
    "fuehrungkompetenz",
    "programmierparadigmen",
]
WISSENSCHAFTLICHESINTERESSE_ATTRS: list[str] = [
    "name",
    "stichwort",
]
WISSENSGEBIET_ATTRS: list[str] = [
    "name",
    "titel",
    "reihenfolge",
    "architekturstil",
    "kategorien",
]
SUBKATEGORIE_ATTRS: list[str] = [
    "typ",
    "items",
]
TECHNOLOGY_ATTRS: list[str] = [
    "name",
    "category",
    "aliases",
    "sfia_levels",
]
SFIALEVEL_ATTRS: list[str] = [
    "years",
    "level",
]
TECHNOLOGYRELATION_ATTRS: list[str] = [
    "name",
    "source",
    "kind",
    "targets",
]
ROLEPROFILE_ATTRS: list[str] = [
    "name",
    "title",
    "sfia_level",
    "sfia_min",
    "sfia_max",
    "description",
    "competencies",
    "abgrenzung",
]
COMPETENCYAREA_ATTRS: list[str] = [
    "area",
    "erwartet",
    "wuenschenswert",
]
PREFERENCE_ATTRS: list[str] = [
    "name",
    "topic",
    "prefer",
    "over",
    "reason",
]
WARNRULE_ATTRS: list[str] = [
    "name",
    "indicators",
    "reason",
]
BOOSTRULE_ATTRS: list[str] = [
    "name",
    "indicators",
    "reason",
]
DEPRIORITIZERULE_ATTRS: list[str] = [
    "name",
    "indicators",
    "reason",
]
