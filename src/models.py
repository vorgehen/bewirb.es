# AUTO-GENERATED -- nicht manuell bearbeiten.
# Quelle: grammar/profile.tx  ->  codegen/codegen.py
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
