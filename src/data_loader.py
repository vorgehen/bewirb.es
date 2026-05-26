from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel
from textx import metamodel_from_file

from src.models import (
    Auftraggeber,
    Ausbildung,
    Branche,
    Kontakt,
    PersoenlicheDaten,
    Person,
    Projekterfahrung,
    Schluesselkompetenzen,
    Sprache,
    Technologiekompetenz,
    Werdegang,
    Zertifikat,
)

GRAMMAR_DIR = Path(__file__).parent.parent / "grammar"


class Profil(BaseModel):
    person: Person
    technologien: list[Technologiekompetenz] = []
    projekte: list[Projekterfahrung] = []
    ausbildungen: list[Ausbildung] = []
    branchen: list[Branche] = []
    auftraggeber_liste: list[Auftraggeber] = []
    sprachen: list[Sprache] = []
    zertifikate: list[Zertifikat] = []
    werdegang: list[Werdegang] = []
    schluesselkompetenzen: Schluesselkompetenzen | None = None


class Anforderungen(BaseModel):
    name: str = ""
    rolle: str = ""
    zielgruppe: str = ""
    branchen: list[str] = []
    must_have: list[str] = []
    nice_to_have: list[str] = []
    keywords: list[str] = []
    context: str = ""
    expires: str = ""


def _to_person(obj: Any) -> Person:
    c = obj.contact
    pd_obj = obj.persoenlicheDaten
    persoenliche_daten: PersoenlicheDaten | None = None
    if pd_obj is not None:
        persoenliche_daten = PersoenlicheDaten(
            geburtsdatum=pd_obj.geburtsdatum or "",
            geburtsort=pd_obj.geburtsort or "",
            staatsangehoerigkeit=pd_obj.staatsangehoerigkeit or "",
            familienstand=pd_obj.familienstand or "",
            kinder=pd_obj.kinder or "",
        )
    return Person(
        name=obj.name or "",
        title=obj.title or "",
        contact=Kontakt(
            email=c.email or "",
            phone=c.phone or "",
            location=c.location or "",
            website=c.website or "",
            linkedin=c.linkedin or "",
            github=c.github or "",
        ),
        kurzprofil=obj.kurzprofil or "",
        persoenlicheDaten=persoenliche_daten,
    )


def _to_sprache(obj: Any) -> Sprache:
    return Sprache(
        name=obj.name or "",
        bezeichnung=obj.bezeichnung or "",
        level=obj.level or "",
    )


def _to_zertifikat(obj: Any) -> Zertifikat:
    return Zertifikat(
        name=obj.name or "",
        titel=obj.titel or "",
        aussteller=obj.aussteller or "",
        jahr=obj.jahr or 0,
        url=obj.url or "",
    )


def _to_werdegang(obj: Any) -> Werdegang:
    return Werdegang(
        name=obj.name or "",
        titel=obj.titel or "",
        arbeitgeber=obj.arbeitgeber or "",
        start=obj.start or "",
        end=obj.end or "",
        beschreibung=obj.beschreibung or "",
    )


def _to_schluesselkompetenzen(obj: Any) -> Schluesselkompetenzen:
    return Schluesselkompetenzen(
        methodenkompetenz=list(obj.methodenkompetenz),
        fachkompetenz=list(obj.fachkompetenz),
        technologie=list(obj.technologie),
        spezialgebiet=list(obj.spezialgebiet),
        fuehrungkompetenz=list(obj.fuehrungkompetenz),
    )


def _to_technologiekompetenz(obj: Any) -> Technologiekompetenz:
    return Technologiekompetenz(
        name=obj.name or "",
        category=obj.category or "",
        proficiency=obj.proficiency or "",
        years=obj.years or 0,
        keywords=list(obj.keywords),
    )


def _to_branche(obj: Any) -> Branche:
    return Branche(name=obj.name or "", label=obj.label or "")


def _to_auftraggeber(obj: Any) -> Auftraggeber:
    return Auftraggeber(
        name=obj.name or "",
        label=obj.label or "",
        location=obj.location or "",
        extern=obj.extern or "",
    )


def _to_projekterfahrung(
    obj: Any,
    branchen_map: dict[str, Branche],
    auftraggeber_map: dict[str, Auftraggeber],
    tech_map: dict[str, Technologiekompetenz],
) -> Projekterfahrung:
    return Projekterfahrung(
        name=obj.name or "",
        title=obj.title or "",
        auftraggeber=auftraggeber_map[obj.auftraggeber.name],
        branche=branchen_map[obj.branche.name],
        start=obj.start or "",
        end=obj.end or "",
        rolle=obj.rolle or "",
        uses=[tech_map[t.name] for t in obj.uses],
        keywords=list(obj.keywords),
        description=obj.description or "",
        achievements=list(obj.achievements),
    )


def _to_ausbildung(obj: Any) -> Ausbildung:
    return Ausbildung(
        name=obj.name or "",
        title=obj.title or "",
        institution=obj.institution or "",
        start=obj.start or "",
        end=obj.end or "",
        abschluss=obj.abschluss or "",
    )


def load_profile(path: Path) -> Profil:
    if not path.exists():
        raise FileNotFoundError(f"Profil-Datei nicht gefunden: {path}")

    mm = metamodel_from_file(str(GRAMMAR_DIR / "profile.tx"))
    model = mm.model_from_file(str(path))

    branchen_map: dict[str, Branche] = {}
    auftraggeber_map: dict[str, Auftraggeber] = {}
    tech_map: dict[str, Technologiekompetenz] = {}
    person: Person | None = None
    ausbildungen: list[Ausbildung] = []
    sprachen: list[Sprache] = []
    zertifikate: list[Zertifikat] = []
    werdegang: list[Werdegang] = []
    schluesselkompetenzen: Schluesselkompetenzen | None = None

    for elem in model.elements:
        cls_name = elem.__class__.__name__
        if cls_name == "Branche":
            b = _to_branche(elem)
            branchen_map[b.name] = b
        elif cls_name == "Auftraggeber":
            a = _to_auftraggeber(elem)
            auftraggeber_map[a.name] = a
        elif cls_name == "Technologiekompetenz":
            t = _to_technologiekompetenz(elem)
            tech_map[t.name] = t
        elif cls_name == "Person":
            person = _to_person(elem)
        elif cls_name == "Ausbildung":
            ausbildungen.append(_to_ausbildung(elem))
        elif cls_name == "Sprache":
            sprachen.append(_to_sprache(elem))
        elif cls_name == "Zertifikat":
            zertifikate.append(_to_zertifikat(elem))
        elif cls_name == "Werdegang":
            werdegang.append(_to_werdegang(elem))
        elif cls_name == "Schluesselkompetenzen":
            schluesselkompetenzen = _to_schluesselkompetenzen(elem)

    projekte: list[Projekterfahrung] = [
        _to_projekterfahrung(elem, branchen_map, auftraggeber_map, tech_map)
        for elem in model.elements
        if elem.__class__.__name__ == "Projekterfahrung"
    ]

    if person is None:
        raise ValueError(f"Keine Person in Profil-Datei gefunden: {path}")

    return Profil(
        person=person,
        technologien=list(tech_map.values()),
        projekte=projekte,
        ausbildungen=ausbildungen,
        branchen=list(branchen_map.values()),
        auftraggeber_liste=list(auftraggeber_map.values()),
        sprachen=sprachen,
        zertifikate=zertifikate,
        werdegang=werdegang,
        schluesselkompetenzen=schluesselkompetenzen,
    )


def load_requirements(path: Path) -> Anforderungen:
    if not path.exists():
        raise FileNotFoundError(f"Anforderungs-Datei nicht gefunden: {path}")

    mm = metamodel_from_file(str(GRAMMAR_DIR / "requirements.tx"))
    model = mm.model_from_file(str(path))

    return Anforderungen(
        name=model.name or "",
        rolle=model.rolle or "",
        zielgruppe=model.zielgruppe or "",
        branchen=list(model.branchen),
        must_have=list(model.must_have),
        nice_to_have=list(model.nice_to_have),
        keywords=list(model.keywords),
        context=model.context or "",
        expires=model.expires or "",
    )
