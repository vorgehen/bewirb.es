from __future__ import annotations

import pytest

from src.data_loader import Anforderungen, Profil
from src.matcher import MatchResult, match_profile_to_requirements
from src.models import Kontakt, Person, Technologiekompetenz

pytestmark = pytest.mark.unit


def _make_profil(techs: list[str]) -> Profil:
    person = Person(name="TestDev", title="Entwickler", contact=Kontakt(email="t@t.de"))
    technologien = [
        Technologiekompetenz(name=t, category="Programmiersprache", proficiency="Experte", years=5)
        for t in techs
    ]
    return Profil(person=person, technologien=technologien)


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
