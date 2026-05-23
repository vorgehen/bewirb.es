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
