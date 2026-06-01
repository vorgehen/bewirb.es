from __future__ import annotations

import re

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


def _term_variants(term: str) -> list[str]:
    """Zerlegt zusammengesetzte Anforderungen in Einzel-Terme.

    'Java oder TypeScript'          → ['java oder typescript', 'java', 'typescript']
    'Spring Boot oder React/Vue'    → ['spring boot oder react/vue', 'spring boot', 'react', 'vue']
    """
    needle = term.lower()
    parts = [
        p.strip() for p in needle.replace("/", " oder ").split(" oder ") if len(p.strip()) >= 3
    ]
    if len(parts) > 1:
        return [needle] + parts
    return [needle]


def _corpus_tokens(corpus: list[str]) -> set[str]:
    """Einzelne Tokens (≥3 Zeichen) aus allen Corpus-Items.

    Trennt an Leerzeichen, Sonderzeichen und Klammern, damit z. B.
    'n-tier · soa · portal · microservices' den Token 'microservices'
    liefert, der dann in 'microservices-architektur' gefunden wird.
    """
    tokens: set[str] = set()
    for item in corpus:
        for tok in re.split(r"[\s·()\[\]/,;:]+", item):
            if len(tok) >= 4:
                tokens.add(tok)
    return tokens


def _matches(term: str, corpus: list[str]) -> bool:
    """Prüft ob ein Anforderungs-Term im Profil-Corpus vorkommt.

    Drei Strategien (OR-verknüpft), jeweils für alle Compound-Varianten:
    1. Direkt:    Variant steckt als Substring in einem Corpus-Item
    2. Token:     ein Corpus-Token (≥3 Zeichen) steckt als Substring in der Variant
    3. Compound:  'oder'/'/' zerlegen und jede Alternative einzeln prüfen
    """
    tokens = _corpus_tokens(corpus)
    for variant in _term_variants(term):
        if any(variant in c for c in corpus):
            return True
        if any(tok in variant for tok in tokens):
            return True
    return False


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
