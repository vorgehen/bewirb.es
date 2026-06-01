from __future__ import annotations

from pydantic import BaseModel

from src.data_loader import Anforderungen, Profil


class MatchResult(BaseModel):
    score: float
    matched_must_have: list[str]
    missing_must_have: list[str]
    matched_nice_to_have: list[str]


def _profile_tech_corpus(profil: Profil) -> list[str]:
    """Lower-case-Strings aus Wissensgebiet-Titeln, Architekturstil und
    Subkategorie-Items.

    Versionsangaben wie „Java (8–17)" bleiben erhalten — der Match nutzt
    Substring-Vergleich, sodass „Java" auch in „Java (8–17)" gefunden wird.
    Architekturstil ist als Halbsatz formuliert (z. B. „N-Tier · SOA ·
    Portal · Microservices") und trägt damit Stil-Begriffe in den Corpus,
    die in den Subkategorie-Items nicht vorkommen.
    """
    corpus: list[str] = []
    for wg in profil.wissensgebiete:
        corpus.append(wg.titel.lower())
        if wg.architekturstil:
            corpus.append(wg.architekturstil.lower())
        for kat in wg.kategorien:
            corpus.extend(item.lower() for item in kat.items)
    return corpus


def _matches(term: str, corpus: list[str]) -> bool:
    needle = term.lower()
    return any(needle in c for c in corpus)


def match_profile_to_requirements(profil: Profil, anf: Anforderungen) -> MatchResult:
    corpus = _profile_tech_corpus(profil)

    matched_must = [t for t in anf.must_have if _matches(t, corpus)]
    missing_must = [t for t in anf.must_have if not _matches(t, corpus)]
    matched_nice = [t for t in anf.nice_to_have if _matches(t, corpus)]

    total = len(anf.must_have)
    score = len(matched_must) / total if total > 0 else 1.0

    return MatchResult(
        score=score,
        matched_must_have=matched_must,
        missing_must_have=missing_must,
        matched_nice_to_have=matched_nice,
    )
