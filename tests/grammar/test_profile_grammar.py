from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from textx.exceptions import TextXSyntaxError

pytestmark = pytest.mark.unit

EXAMPLE_PROFILE = Path(__file__).parent.parent.parent / "data" / "example" / "example.profile"


def test_valid_minimal_profile(profile_mm: Any, tmp_path: Path) -> None:
    content = """
    branche IT { label: "IT" }
    auftraggeber A { label: "Firma A" }
    technology Python { category: Programmiersprache proficiency: Experte years: 5 }
    person P { title: "Dev" contact { email: "x@x.de" } }
    """
    f = tmp_path / "test.profile"
    f.write_text(content, encoding="utf-8")
    model = profile_mm.model_from_file(str(f))
    assert model is not None


def test_technologiekompetenz_attributes(profile_mm: Any, tmp_path: Path) -> None:
    content = """
    technology Java {
        category: Programmiersprache
        proficiency: Experte
        years: 20
        keywords: ["Java", "Spring"]
    }
    """
    f = tmp_path / "t.profile"
    f.write_text(content, encoding="utf-8")
    model = profile_mm.model_from_file(str(f))
    techs = [e for e in model.elements if e.__class__.__name__ == "Technologiekompetenz"]
    assert len(techs) == 1
    java = techs[0]
    assert java.name == "Java"
    assert java.years == 20
    assert java.proficiency == "Experte"
    assert "Spring" in java.keywords


def test_projekterfahrung_cross_references(mini_profile: Any) -> None:
    projekte = [e for e in mini_profile.elements if e.__class__.__name__ == "Projekterfahrung"]
    assert len(projekte) == 1
    p = projekte[0]
    assert p.name == "TestProjekt"
    assert p.auftraggeber.name == "TestGmbH"
    assert p.branche.name == "IT"
    assert p.start == "2023-01"
    assert p.end == "today"
    assert len(p.uses) == 1
    assert p.uses[0].name == "Python"


def test_optional_fields_default_empty(mini_profile: Any) -> None:
    projekte = [e for e in mini_profile.elements if e.__class__.__name__ == "Projekterfahrung"]
    p = projekte[0]
    assert p.description == ""
    assert p.achievements == []


def test_invalid_category_rejected(profile_mm: Any, tmp_path: Path) -> None:
    content = """
    technology X {
        category: UngueltigeKategorie
        proficiency: Experte
        years: 1
    }
    """
    f = tmp_path / "bad.profile"
    f.write_text(content, encoding="utf-8")
    with pytest.raises(TextXSyntaxError):
        profile_mm.model_from_file(str(f))


def test_invalid_proficiency_rejected(profile_mm: Any, tmp_path: Path) -> None:
    content = """
    technology X {
        category: Programmiersprache
        proficiency: Superexperte
        years: 1
    }
    """
    f = tmp_path / "bad2.profile"
    f.write_text(content, encoding="utf-8")
    with pytest.raises(TextXSyntaxError):
        profile_mm.model_from_file(str(f))


def test_example_profile_parses(profile_mm: Any) -> None:
    model = profile_mm.model_from_file(str(EXAMPLE_PROFILE))
    assert model is not None
    persons = [e for e in model.elements if e.__class__.__name__ == "Person"]
    assert len(persons) == 1
    projekte = [e for e in model.elements if e.__class__.__name__ == "Projekterfahrung"]
    assert len(projekte) >= 1


def test_ausbildung_parses(profile_mm: Any, tmp_path: Path) -> None:
    content = """
    ausbildung Studium {
        title: "Informatik (M.Sc.)"
        institution: "TU Beispiel"
        periode: 2005-10 to 2010-09
        abschluss: "Master of Science"
    }
    """
    f = tmp_path / "ausb.profile"
    f.write_text(content, encoding="utf-8")
    model = profile_mm.model_from_file(str(f))
    ausb = [e for e in model.elements if e.__class__.__name__ == "Ausbildung"]
    assert len(ausb) == 1
    assert ausb[0].start == "2005-10"
    assert ausb[0].end == "2010-09"


# ─── Phase 8: neue Entitäten ────────────────────────────────────────────────


def test_person_with_kurzprofil_and_persoenliche_daten(profile_mm: Any, tmp_path: Path) -> None:
    content = """
    person P {
        title: "Software Engineer"
        contact { email: "x@x.de" }
        kurzprofil: "Diplom-Physiker mit 30 Jahren Erfahrung."
        persoenlicheDaten {
            geburtsdatum: "1962-09-12"
            staatsangehoerigkeit: "Deutsch"
            familienstand: "Verheiratet"
        }
    }
    """
    f = tmp_path / "p.profile"
    f.write_text(content, encoding="utf-8")
    model = profile_mm.model_from_file(str(f))
    p = next(e for e in model.elements if e.__class__.__name__ == "Person")
    assert p.kurzprofil.startswith("Diplom-Physiker")
    assert p.persoenlicheDaten is not None
    assert p.persoenlicheDaten.staatsangehoerigkeit == "Deutsch"


def test_sprache_parses_and_level_enum_enforced(profile_mm: Any, tmp_path: Path) -> None:
    content = """
    sprache deutsch {
        bezeichnung: "Deutsch"
        level: Muttersprache
    }
    sprache englisch {
        bezeichnung: "Englisch"
        level: Verhandlungssicher
    }
    """
    f = tmp_path / "s.profile"
    f.write_text(content, encoding="utf-8")
    model = profile_mm.model_from_file(str(f))
    sprachen = [e for e in model.elements if e.__class__.__name__ == "Sprache"]
    assert len(sprachen) == 2
    assert sprachen[0].level == "Muttersprache"


def test_sprache_invalid_level_rejected(profile_mm: Any, tmp_path: Path) -> None:
    content = """
    sprache deutsch {
        bezeichnung: "Deutsch"
        level: Fließend
    }
    """
    f = tmp_path / "s.profile"
    f.write_text(content, encoding="utf-8")
    with pytest.raises(TextXSyntaxError):
        profile_mm.model_from_file(str(f))


def test_zertifikat_parses(profile_mm: Any, tmp_path: Path) -> None:
    content = """
    zertifikat mitx_stat {
        titel: "Fundamentals of Statistics"
        aussteller: "MITx"
        jahr: 2019
    }
    """
    f = tmp_path / "z.profile"
    f.write_text(content, encoding="utf-8")
    model = profile_mm.model_from_file(str(f))
    zerts = [e for e in model.elements if e.__class__.__name__ == "Zertifikat"]
    assert len(zerts) == 1
    assert zerts[0].jahr == 2019


def test_werdegang_parses(profile_mm: Any, tmp_path: Path) -> None:
    content = """
    werdegang freiberuflich {
        titel: "Freiberuflicher Software Ingenieur"
        arbeitgeber: "vorgehen.de"
        periode: 2010-04 to today
        beschreibung: "Langfristige Projekte bei DAX-Konzernen und Behörden."
    }
    """
    f = tmp_path / "w.profile"
    f.write_text(content, encoding="utf-8")
    model = profile_mm.model_from_file(str(f))
    wd = [e for e in model.elements if e.__class__.__name__ == "Werdegang"]
    assert len(wd) == 1
    assert wd[0].arbeitgeber == "vorgehen.de"
    assert wd[0].end == "today"


def test_schluesselkompetenzen_all_five_categories(profile_mm: Any, tmp_path: Path) -> None:
    content = """
    schluesselkompetenzen {
        methodenkompetenz: ["MDD", "TDD"]
        fachkompetenz: ["Finanzaufsicht"]
        technologie: ["Java", "Xtext"]
        spezialgebiet: ["DSL-Design"]
        fuehrungkompetenz: ["Stakeholder-Management"]
    }
    """
    f = tmp_path / "sk.profile"
    f.write_text(content, encoding="utf-8")
    model = profile_mm.model_from_file(str(f))
    sk = next(e for e in model.elements if e.__class__.__name__ == "Schluesselkompetenzen")
    assert "MDD" in sk.methodenkompetenz
    assert "Xtext" in sk.technologie
    assert "Stakeholder-Management" in sk.fuehrungkompetenz


def test_schluesselkompetenzen_all_categories_optional(profile_mm: Any, tmp_path: Path) -> None:
    """Leere Schluesselkompetenzen sind erlaubt — alle Felder optional."""
    content = """
    schluesselkompetenzen {
    }
    """
    f = tmp_path / "sk_empty.profile"
    f.write_text(content, encoding="utf-8")
    model = profile_mm.model_from_file(str(f))
    sk = next(e for e in model.elements if e.__class__.__name__ == "Schluesselkompetenzen")
    assert sk.methodenkompetenz == []
    assert sk.technologie == []
