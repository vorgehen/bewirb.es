# AUTO-GENERATED -- nicht manuell bearbeiten.
# Quelle: grammar/{profile.tx, knowledge.tx}  ->  codegen/codegen.py

NODE_TYPES: list[str] = [
    "Person",
    "Kontakt",
    "Technologiekompetenz",
    "Branche",
    "Auftraggeber",
    "Projekterfahrung",
    "Ausbildung",
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
