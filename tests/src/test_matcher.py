from __future__ import annotations

import pytest

from src.data_loader import Anforderungen, Profil
from src.matcher import MatchResult, match_profile_to_requirements
from src.models import Kontakt, Person, Subkategorie, Wissensgebiet

pytestmark = pytest.mark.unit


def _make_profil(techs: list[str]) -> Profil:
    """Profil mit einem Wissensgebiet, dessen Sprache-Kategorie alle techs enthält."""
    person = Person(name="TestDev", title="Entwickler", contact=Kontakt(email="t@t.de"))
    wg = Wissensgebiet(
        name="wg_test",
        titel="Test-Wissensgebiet",
        reihenfolge=1,
        kategorien=[Subkategorie(typ="Sprache", items=techs)],
    )
    return Profil(person=person, wissensgebiete=[wg])


def _make_anforderungen(must: list[str], nice: list[str]) -> Anforderungen:
    return Anforderungen(rolle="Entwickler", must_have=must, nice_to_have=nice)


def test_full_match_score_is_1() -> None:
    profil = _make_profil(["Python", "Django"])
    anf = _make_anforderungen(["Python", "Django"], [])
    result = match_profile_to_requirements(profil, anf)
    assert result.score == 1.0


def test_no_match_score_is_0() -> None:
    profil = _make_profil(["Java"])
    anf = _make_anforderungen(["Python", "Django"], [])
    result = match_profile_to_requirements(profil, anf)
    assert result.score == 0.0


def test_partial_match_score_between_0_and_1() -> None:
    profil = _make_profil(["Python"])
    anf = _make_anforderungen(["Python", "Django"], [])
    result = match_profile_to_requirements(profil, anf)
    assert 0.0 < result.score < 1.0


def test_matched_must_have() -> None:
    profil = _make_profil(["Python", "Java"])
    anf = _make_anforderungen(["Python", "Django"], [])
    result = match_profile_to_requirements(profil, anf)
    assert "Python" in result.matched_must_have
    assert "Django" not in result.matched_must_have


def test_missing_must_have() -> None:
    profil = _make_profil(["Python"])
    anf = _make_anforderungen(["Python", "Django"], [])
    result = match_profile_to_requirements(profil, anf)
    assert "Django" in result.missing_must_have


def test_nice_to_have_matched() -> None:
    profil = _make_profil(["Python", "Kotlin"])
    anf = _make_anforderungen(["Python"], ["Kotlin", "Scala"])
    result = match_profile_to_requirements(profil, anf)
    assert "Kotlin" in result.matched_nice_to_have


def test_match_result_has_score_field() -> None:
    result = MatchResult(
        score=0.5,
        matched_must_have=["Python"],
        missing_must_have=["Django"],
        matched_nice_to_have=[],
    )
    assert result.score == 0.5


def test_match_findet_substring_in_versionsangabe() -> None:
    """„Java (8–17)" matched „Java" — Versionsangaben sind unschädlich."""
    profil = _make_profil(["Java (8–17)"])
    anf = _make_anforderungen(["Java"], [])
    result = match_profile_to_requirements(profil, anf)
    assert result.score == 1.0
