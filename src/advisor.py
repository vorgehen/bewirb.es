"""Advisory Layer — bewertet Bewerbungs-Match mit Knowledge-Layer-Unterstützung.

Phase 8a (M2): Modi 1 (Einzel-Angebot) + 2 (Portfolio-Scan).
Phase 8a (M3, später): Modi 3 (Marktpositionierung) + 4 (Profil-Diagnose).

Kein Claude-API-Call in dieser Etappe — alle Bewertungen sind deterministisch
aus Profil + Anforderungen + Knowledge ableitbar.
"""

from __future__ import annotations

import logging
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel
from textx.exceptions import TextXError

from src.data_loader import Anforderungen, Profil, load_profile, load_requirements
from src.knowledge_loader import KnowledgeBase, load_knowledge_base

_log = logging.getLogger(__name__)


class GapType(StrEnum):
    """Vier Klassen von Lücken nach Schließbarkeit."""

    ARTIKULATION = "Artikulations-Lücke"  # vorhanden, nicht kommuniziert
    ZERTIFIZIERUNG = "Zertifizierungs-Lücke"  # >70% Überlappung mit vorhandenem Wissen
    ERFAHRUNG = "Erfahrungs-Lücke"  # fehlt, mittelfristig erlernbar
    STRUKTURELL = "Strukturelle Lücke"  # fundamental fehlend


class Gap(BaseModel):
    term: str
    type: GapType
    reason: str = ""
    schliessbar: bool = True


class AdvisoryResult(BaseModel):
    score: float
    empfehlung: str  # "✓ Bewerbung empfohlen" | "⚠ bedingt" | "✗ nicht empfohlen"
    matched_must_have: list[str] = []
    matched_nice_to_have: list[str] = []
    gaps: list[Gap] = []
    # Stärken die im Profil-Text auftauchen aber nicht als eigene technology
    strengths_underused: list[str] = []
    warnings: list[str] = []  # aus opinions.warn_rules
    boosts: list[str] = []  # aus opinions.boost_rules


# ─── Profil-Text-Index ──────────────────────────────────────────────────────


def _profile_text_index(profil: Profil) -> str:
    """Konkateniert alle Profil-Texte für schnelle Substring-Suche (lowercase)."""
    parts: list[str] = []
    parts.append(profil.person.title)
    parts.append(profil.person.kurzprofil)
    for t in profil.technologien:
        parts.append(t.name)
        parts.extend(t.keywords)
    for p in profil.projekte:
        parts.append(p.title)
        parts.append(p.description)
        parts.append(p.rolle)
        parts.extend(p.keywords)
        parts.extend(p.achievements)
    for w in profil.werdegang:
        parts.extend([w.titel, w.beschreibung, w.arbeitgeber])
    sk = profil.schluesselkompetenzen
    if sk is not None:
        for cat in (
            sk.methodenkompetenz,
            sk.fachkompetenz,
            sk.technologie,
            sk.spezialgebiet,
            sk.fuehrungkompetenz,
        ):
            parts.extend(cat)
    return " ".join(p for p in parts if p).lower()


def _profile_tech_set(profil: Profil, kb: KnowledgeBase) -> set[str]:
    """Normalisierte Tech-Namen im Profil (Profil-IDs durch Knowledge-Aliase aufgelöst)."""
    result: set[str] = set()
    for t in profil.technologien:
        canon = kb.normalize(t.name) or t.name
        result.add(canon.lower())
    return result


# ─── Lücken-Klassifikation ──────────────────────────────────────────────────


def classify_gap(term: str, profil: Profil, kb: KnowledgeBase) -> Gap:
    """Entscheidet welche Schließbarkeits-Klasse für einen fehlenden Begriff gilt."""
    term_lower = term.lower()
    profile_text = _profile_text_index(profil)
    profile_techs = _profile_tech_set(profil, kb)

    canon = kb.normalize(term) or term

    # 1. ARTIKULATION: Begriff oder Alias taucht irgendwo im Profil-Text auf,
    #    aber nicht als eigenständige Technology
    if canon.lower() not in profile_techs and term_lower in profile_text:
        return Gap(
            term=term,
            type=GapType.ARTIKULATION,
            reason=f"Im Profil-Text gefunden ({term!r}), aber kein eigener technology-Eintrag",
            schliessbar=True,
        )

    # 2. ZERTIFIZIERUNG: gibt es eine überschneidet_sich_mit / impliziert-Relation
    #    zu einer Tech die wir haben?
    related_kinds = ("ueberschneidet_sich_mit", "impliziert", "erweitert")
    for rel in kb.relations:
        rel_source_lower = rel.source.lower()
        if (
            rel_source_lower in profile_techs
            and rel.kind in related_kinds
            and any(t.lower() == term_lower or t.lower() == canon.lower() for t in rel.targets)
        ):
            return Gap(
                term=term,
                type=GapType.ZERTIFIZIERUNG,
                reason=f"Verwandt zu vorhandener Kompetenz {rel.source!r} ({rel.kind})",
                schliessbar=True,
            )

    # 3. ERFAHRUNG vs. STRUKTURELL: Heuristik — wenn Knowledge die Tech kennt
    #    (oder mit unseren Aliasen normalisierbar), klassifizieren wir als
    #    Erfahrungslücke (in Monaten lernbar). Sonst strukturell.
    if kb.technology_by_name(canon) is not None:
        return Gap(
            term=term,
            type=GapType.ERFAHRUNG,
            reason=f"Technology {canon!r} im Knowledge Layer bekannt, aber nicht im Profil",
            schliessbar=True,
        )

    return Gap(
        term=term,
        type=GapType.STRUKTURELL,
        reason=f"Begriff {term!r} weder im Profil noch im Knowledge Layer",
        schliessbar=False,
    )


# ─── Opinion-Auswertung ────────────────────────────────────────────────────


def _trigger_opinion_rules(
    indicators_pool: list[str], rules: list[dict[str, list[str] | str]]
) -> list[str]:
    """Findet alle Regeln deren Indikatoren im Indicator-Pool vorkommen.

    indicators_pool ist eine Liste lowercase-Strings (z.B. Anforderungs-Keywords).
    Gibt die Reason-Texte der getriggerten Regeln zurück.
    """
    pool = [s.lower() for s in indicators_pool]
    triggered: list[str] = []
    for rule in rules:
        rule_indicators = rule.get("indicators", [])
        if not isinstance(rule_indicators, list):
            continue
        for ind in rule_indicators:
            ind_lower = ind.lower()
            if any(ind_lower in p for p in pool):
                reason = rule.get("reason", "")
                if isinstance(reason, str) and reason:
                    triggered.append(reason)
                break
    return triggered


def _anf_indicator_pool(anf: Anforderungen) -> list[str]:
    """Sammelt alle Strings aus Anforderungen für Opinion-Matching."""
    return [
        anf.rolle,
        anf.context,
        *anf.must_have,
        *anf.nice_to_have,
        *anf.keywords,
        *anf.branchen,
    ]


# ─── Hauptbewertung ────────────────────────────────────────────────────────


def _verdict(score: float, structural_gaps: int) -> str:
    if structural_gaps > 0:
        return "✗ nicht empfohlen"
    if score >= 0.80:
        return "✓ Bewerbung empfohlen"
    if score >= 0.50:
        return "⚠ bedingt"
    return "✗ nicht empfohlen"


def evaluate_offer(profil: Profil, anf: Anforderungen, kb: KnowledgeBase) -> AdvisoryResult:
    """Bewertet ein einzelnes Stellenangebot gegen das Profil + Knowledge."""
    profile_techs = _profile_tech_set(profil, kb)

    matched_must: list[str] = []
    missing_must: list[str] = []
    for term in anf.must_have:
        canon = kb.normalize(term) or term
        if canon.lower() in profile_techs:
            matched_must.append(term)
        else:
            missing_must.append(term)

    matched_nice = [
        term for term in anf.nice_to_have if (kb.normalize(term) or term).lower() in profile_techs
    ]

    gaps = [classify_gap(term, profil, kb) for term in missing_must]

    # Strukturelle Lücken senken den Score automatisch via _verdict;
    # Artikulations-Lücken werden hier zu Stärken-Hinweisen (das fehlt nur im
    # tech-Eintrag, ist aber im Profil-Text).
    strengths_underused: list[str] = []
    for gap in gaps:
        if gap.type == GapType.ARTIKULATION:
            strengths_underused.append(
                f"{gap.term}: im Profil-Text vorhanden, aber kein eigenständiger "
                f"technology-Eintrag — Artikulation schärfen"
            )

    total = len(anf.must_have)
    raw_score = len(matched_must) / total if total > 0 else 1.0
    # Artikulations-Lücken zählen halb mit (vorhanden, nur nicht artikuliert)
    artikulation_count = sum(1 for g in gaps if g.type == GapType.ARTIKULATION)
    effective_score = raw_score + (0.5 * artikulation_count / total if total > 0 else 0)
    effective_score = min(1.0, effective_score)

    structural_count = sum(1 for g in gaps if g.type == GapType.STRUKTURELL)

    pool = _anf_indicator_pool(anf)
    warnings = _trigger_opinion_rules(pool, kb.opinions.warn_rules)
    boosts = _trigger_opinion_rules(pool, kb.opinions.boost_rules)
    deprio = _trigger_opinion_rules(pool, kb.opinions.deprioritize_rules)
    if deprio:
        warnings.extend(f"[depriorisiert] {r}" for r in deprio)

    return AdvisoryResult(
        score=effective_score,
        empfehlung=_verdict(effective_score, structural_count),
        matched_must_have=matched_must,
        matched_nice_to_have=matched_nice,
        gaps=gaps,
        strengths_underused=strengths_underused,
        warnings=warnings,
        boosts=boosts,
    )


# ─── Portfolio-Scan ────────────────────────────────────────────────────────


class PortfolioEntry(BaseModel):
    file: str  # nur Dateiname
    score: float
    empfehlung: str
    missing_must_have: list[str] = []


class PortfolioScan(BaseModel):
    entries: list[PortfolioEntry] = []  # absteigend nach Score
    recurring_gaps: list[tuple[str, int]] = []  # (Begriff, Anzahl Angebote)

    def top(self, n: int = 5) -> list[PortfolioEntry]:
        return self.entries[:n]


def scan_offers(profil_path: Path, offers_dir: Path) -> PortfolioScan:
    """Scannt alle .req-Dateien in offers_dir und rankt sie nach Match-Score."""
    profil = load_profile(profil_path)
    kb = load_knowledge_base()

    entries: list[PortfolioEntry] = []
    gap_counter: dict[str, int] = {}

    for req_path in sorted(offers_dir.rglob("*.req")):
        try:
            anf = load_requirements(req_path)
        except (TextXError, FileNotFoundError, OSError) as e:
            _log.warning("Konnte %s nicht laden: %s", req_path, e)
            continue
        result = evaluate_offer(profil, anf, kb)
        entries.append(
            PortfolioEntry(
                file=req_path.name,
                score=result.score,
                empfehlung=result.empfehlung,
                missing_must_have=[g.term for g in result.gaps],
            )
        )
        for g in result.gaps:
            gap_counter[g.term] = gap_counter.get(g.term, 0) + 1

    entries.sort(key=lambda e: e.score, reverse=True)
    recurring = sorted(
        [(term, count) for term, count in gap_counter.items() if count >= 2],
        key=lambda x: -x[1],
    )
    return PortfolioScan(entries=entries, recurring_gaps=recurring)
