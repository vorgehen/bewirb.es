from __future__ import annotations

from pathlib import Path

import pytest

from src.data_loader import load_profile, load_requirements

pytestmark = pytest.mark.unit

EXAMPLE_PROFILE = Path(__file__).parent.parent.parent / "data" / "example" / "example.profile"
EXAMPLE_REQ = Path(__file__).parent.parent.parent / "data" / "example" / "example_job.req"


def test_load_profile_returns_person() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    assert profil.person.title != ""


def test_load_profile_has_projekte() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    assert len(profil.projekte) >= 1


def test_load_profile_has_technologien() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    assert len(profil.technologien) >= 1


def test_load_profile_has_ausbildungen() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    assert len(profil.ausbildungen) >= 1


def test_load_profile_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_profile(Path("nicht_vorhanden.profile"))


def test_load_requirements_rolle() -> None:
    anf = load_requirements(EXAMPLE_REQ)
    assert anf.rolle != ""


def test_load_requirements_must_have() -> None:
    anf = load_requirements(EXAMPLE_REQ)
    assert len(anf.must_have) >= 1


def test_load_requirements_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_requirements(Path("nicht_vorhanden.req"))


# ─── Phase 8b: neue Entitäten ───────────────────────────────────────────────


def test_load_profile_person_kurzprofil() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    assert profil.person.kurzprofil != ""


def test_load_profile_person_persoenliche_daten() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    pd = profil.person.persoenlicheDaten
    assert pd is not None
    assert pd.staatsangehoerigkeit == "Deutsch"
    assert pd.familienstand == "Verheiratet"


def test_load_profile_sprachen() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    assert len(profil.sprachen) >= 2
    levels = {s.level for s in profil.sprachen}
    assert "Muttersprache" in levels


def test_load_profile_zertifikate() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    assert len(profil.zertifikate) >= 1
    aussteller = {z.aussteller for z in profil.zertifikate}
    assert "iSAQB" in aussteller


def test_load_profile_werdegang() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    assert len(profil.werdegang) >= 1
    arbeitgeber = [w.arbeitgeber for w in profil.werdegang]
    assert any("GmbH" in a or "AG" in a for a in arbeitgeber)


def test_load_profile_schluesselkompetenzen() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    sk = profil.schluesselkompetenzen
    assert sk is not None
    assert "Java" in sk.technologie
    assert len(sk.methodenkompetenz) >= 1
    assert len(sk.fuehrungkompetenz) >= 1


def test_load_requirements_zielgruppe_default_leer() -> None:
    """example_job.req hat keine Zielgruppe — Default-Wert leer."""
    anf = load_requirements(EXAMPLE_REQ)
    assert anf.zielgruppe == ""


def test_load_requirements_zielgruppe_geladen(tmp_path: Path) -> None:
    content = """
    requirements R {
        rolle: "Test"
        zielgruppe: Consultant
        must_have: ["Java"]
    }
    """
    f = tmp_path / "zg.req"
    f.write_text(content, encoding="utf-8")
    anf = load_requirements(f)
    assert anf.zielgruppe == "Consultant"
