# AUTO-GENERATED -- nicht manuell bearbeiten.
# Quelle: grammar/{profile.tx, knowledge.tx}  ->  codegen/codegen.py
from __future__ import annotations

from pydantic import BaseModel


class PersonResponse(BaseModel):
    name: str = ""
    title: str = ""
    contact: KontaktResponse


class KontaktResponse(BaseModel):
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    linkedin: str = ""
    github: str = ""


class TechnologiekompetenzResponse(BaseModel):
    name: str = ""
    category: str = ""
    proficiency: str = ""
    years: int
    keywords: list[str] = []


class BrancheResponse(BaseModel):
    name: str = ""
    label: str = ""


class AuftraggeberResponse(BaseModel):
    name: str = ""
    label: str = ""
    location: str = ""


class ProjekterfahrungResponse(BaseModel):
    name: str = ""
    title: str = ""
    auftraggeber: AuftraggeberResponse
    branche: BrancheResponse
    start: str = ""
    end: str = ""
    rolle: str = ""
    uses: list[TechnologiekompetenzResponse] = []
    keywords: list[str] = []
    description: str = ""
    achievements: list[str] = []


class AusbildungResponse(BaseModel):
    name: str = ""
    title: str = ""
    institution: str = ""
    start: str = ""
    end: str = ""
    abschluss: str = ""


class TechnologyResponse(BaseModel):
    name: str = ""
    category: str = ""
    aliases: list[str] = []
    sfia_levels: list[SfiaLevelResponse] = []


class SfiaLevelResponse(BaseModel):
    years: int
    level: int


class TechnologyRelationResponse(BaseModel):
    name: str = ""
    source: TechnologyResponse
    kind: str = ""
    targets: list[str] = []


class RoleProfileResponse(BaseModel):
    name: str = ""
    title: str = ""
    sfia_level: int
    sfia_min: int
    sfia_max: int
    description: str = ""
    competencies: list[CompetencyAreaResponse] = []
    abgrenzung: list[str] = []


class CompetencyAreaResponse(BaseModel):
    area: str = ""
    erwartet: list[str] = []
    wuenschenswert: list[str] = []


class PreferenceResponse(BaseModel):
    name: str = ""
    topic: str = ""
    prefer: str = ""
    over: str = ""
    reason: str = ""


class WarnRuleResponse(BaseModel):
    name: str = ""
    indicators: list[str] = []
    reason: str = ""


class BoostRuleResponse(BaseModel):
    name: str = ""
    indicators: list[str] = []
    reason: str = ""


class DeprioritizeRuleResponse(BaseModel):
    name: str = ""
    indicators: list[str] = []
    reason: str = ""
