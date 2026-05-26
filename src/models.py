# AUTO-GENERATED -- nicht manuell bearbeiten.
# Quelle: grammar/{profile.tx, knowledge.tx}  ->  codegen/codegen.py
from __future__ import annotations

from pydantic import BaseModel


class Person(BaseModel):
    name: str = ""
    title: str = ""
    contact: Kontakt
    kurzprofil: str = ""
    persoenlicheDaten: PersoenlicheDaten | None = None


class PersoenlicheDaten(BaseModel):
    geburtsdatum: str = ""
    geburtsort: str = ""
    staatsangehoerigkeit: str = ""
    familienstand: str = ""
    kinder: str = ""


class Kontakt(BaseModel):
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    linkedin: str = ""
    github: str = ""


class Technologiekompetenz(BaseModel):
    name: str = ""
    category: str = ""
    proficiency: str = ""
    years: int
    keywords: list[str] = []


class Branche(BaseModel):
    name: str = ""
    label: str = ""


class Auftraggeber(BaseModel):
    name: str = ""
    label: str = ""
    location: str = ""
    extern: str = ""


class Projekterfahrung(BaseModel):
    name: str = ""
    title: str = ""
    auftraggeber: Auftraggeber
    branche: Branche
    start: str = ""
    end: str = ""
    rolle: str = ""
    uses: list[Technologiekompetenz] = []
    keywords: list[str] = []
    description: str = ""
    achievements: list[str] = []


class Ausbildung(BaseModel):
    name: str = ""
    title: str = ""
    institution: str = ""
    start: str = ""
    end: str = ""
    abschluss: str = ""


class Sprache(BaseModel):
    name: str = ""
    bezeichnung: str = ""
    level: str = ""


class Zertifikat(BaseModel):
    name: str = ""
    titel: str = ""
    aussteller: str = ""
    jahr: int
    url: str = ""


class Werdegang(BaseModel):
    name: str = ""
    titel: str = ""
    arbeitgeber: str = ""
    start: str = ""
    end: str = ""
    beschreibung: str = ""


class Schluesselkompetenzen(BaseModel):
    methodenkompetenz: list[str] = []
    fachkompetenz: list[str] = []
    technologie: list[str] = []
    spezialgebiet: list[str] = []
    fuehrungkompetenz: list[str] = []


class Technology(BaseModel):
    name: str = ""
    category: str = ""
    aliases: list[str] = []
    sfia_levels: list[SfiaLevel] = []


class SfiaLevel(BaseModel):
    years: int
    level: int


class TechnologyRelation(BaseModel):
    name: str = ""
    source: Technology
    kind: str = ""
    targets: list[str] = []


class RoleProfile(BaseModel):
    name: str = ""
    title: str = ""
    sfia_level: int
    sfia_min: int
    sfia_max: int
    description: str = ""
    competencies: list[CompetencyArea] = []
    abgrenzung: list[str] = []


class CompetencyArea(BaseModel):
    area: str = ""
    erwartet: list[str] = []
    wuenschenswert: list[str] = []


class Preference(BaseModel):
    name: str = ""
    topic: str = ""
    prefer: str = ""
    over: str = ""
    reason: str = ""


class WarnRule(BaseModel):
    name: str = ""
    indicators: list[str] = []
    reason: str = ""


class BoostRule(BaseModel):
    name: str = ""
    indicators: list[str] = []
    reason: str = ""


class DeprioritizeRule(BaseModel):
    name: str = ""
    indicators: list[str] = []
    reason: str = ""
