from __future__ import annotations

from pydantic import BaseModel

from src.data_loader import Anforderungen, Profil


class MatchResult(BaseModel):
    score: float
    matched_must_have: list[str]
    missing_must_have: list[str]
    matched_nice_to_have: list[str]


def match_profile_to_requirements(profil: Profil, anf: Anforderungen) -> MatchResult:
    tech_names = {t.name.lower() for t in profil.technologien}

    matched_must = [t for t in anf.must_have if t.lower() in tech_names]
    missing_must = [t for t in anf.must_have if t.lower() not in tech_names]
    matched_nice = [t for t in anf.nice_to_have if t.lower() in tech_names]

    total = len(anf.must_have)
    score = len(matched_must) / total if total > 0 else 1.0

    return MatchResult(
        score=score,
        matched_must_have=matched_must,
        missing_must_have=missing_must,
        matched_nice_to_have=matched_nice,
    )
