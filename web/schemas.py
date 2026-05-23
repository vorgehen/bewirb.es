# AUTO-GENERATED -- nicht manuell bearbeiten.
# Quelle: grammar/profile.tx  ->  codegen/codegen.py
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
