# AUTO-GENERATED -- nicht manuell bearbeiten.
# Quelle: grammar/{profile.tx, knowledge.tx}  ->  codegen/codegen.py
from __future__ import annotations

from pydantic import BaseModel


class Person(BaseModel):
    name: str = ""
    title: str = ""
    contact: Kontakt


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
