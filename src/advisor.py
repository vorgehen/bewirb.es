"""Advisory Layer — bewertet Bewerbungs-Match mit Knowledge-Layer-Unterstützung.

Phase 8a (M2): Modi 1 (Einzel-Angebot) + 2 (Portfolio-Scan).
Phase 8a (M3, später): Modi 3 (Marktpositionierung) + 4 (Profil-Diagnose).

Kein Claude-API-Call in dieser Etappe — alle Bewertungen sind deterministisch
aus Profil + Anforderungen + Knowledge ableitbar.
"""

from __future__ import annotations

import logging
import re
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel
from textx.exceptions import TextXError

from src.data_loader import Anforderungen, Profil, load_profile, load_requirements
from src.knowledge_loader import KnowledgeBase, load_knowledge_base

_log = logging.getLogger(__name__)


# Gender-Marker: Architekt*in, Architekt:in, Architekt_in, Architekt/in,
# Architekt*innen, Architekt:innen, Architekt/innen
_GENDER_SUFFIX_RE = re.compile(r"([\*:/_])innen\b|([\*:/_])in\b", re.IGNORECASE)
# Weibliche -in Endung (Architektin, Entwicklerin): konservativ nur nach
# bestimmten Stämmen — naives Suffix-Stripping würde zu viele False-Positives
# liefern ("Maschine", "Limousine"). Hier nur expliziert für übliche Rollen-Stämme.
_FEMALE_ENDING_RE = re.compile(
    r"\b(\w*(?:arbeiter|architekt|berater|consultant|developer|engineer|"
    r"entwickler|expert|ingenieur|leiter|manager|programmierer|spezialist))in(?:nen)?\b",
    re.IGNORECASE,
)


def _normalize_gender(text: str) -> str:
    """Entfernt Gender-Marker (*in, :in, /in, _in, *innen) und ersetzt
    weibliche -in/-innen-Endungen bei klaren Rollen-Stämmen durch maskuline Form.
    """
    text = _GENDER_SUFFIX_RE.sub("", text)
    text = _FEMALE_ENDING_RE.sub(r"\1", text)
    return text


# ─── Soft-Requirement-Erkennung ────────────────────────────────────────────
#
# Soft-Requirements sind must_have-Einträge die formal als Anforderung gelistet
# sind, aber keine technischen Skills — sondern formale, organisatorische oder
# rechtliche Voraussetzungen (Sprachen, Staatsangehörigkeit, Sicherheits-
# überprüfung, Hochschulabschluss, pauschale Berufserfahrung, Soft Skills,
# Reisebereitschaft).
#
# Sie werden aus dem Score-Nenner ausgeschlossen und separat angezeigt
# (Selbst-Check).

_SOFT_REQUIREMENT_PATTERNS = [
    # Sprachen DE: GER-Niveau, C1/C2/B1/B2, oder "Deutsch/Englisch ... Niveau/Kenntnisse"
    (r"\b(GER|C[12]|B[12]|A[12])\b", "Sprachkenntnisse"),
    (
        r"\b(Deutsch|Englisch|Französisch|Spanisch)\b.{0,30}\b"
        r"(kenntnisse|niveau|fließend|Mutter|verhandlungssicher|fluently)\b",
        "Sprachkenntnisse",
    ),
    # Sprachen EN: "English proficiency", "Fluent in English", "Native German speaker"
    (
        r"\b(English|German|French|Spanish)\s+(proficiency|fluency|skills?|level|native)\b",
        "Sprachkenntnisse",
    ),
    (
        r"\b(Fluent|Native|Proficient)\s+(in\s+)?(English|German|French|Spanish)\b",
        "Sprachkenntnisse",
    ),
    # Sicherheit
    (r"\bSicherheits(überprüfung|prüfung|check)\b", "Sicherheitsfreigabe"),
    (r"\bFührungszeugnis\b", "Sicherheitsfreigabe"),
    (r"\b(security\s+clearance|background\s+check)\b", "Sicherheitsfreigabe"),
    # Staatsangehörigkeit
    (
        r"\b(Staatsangehörigkeit|Staatsbürgerschaft|EU[-/ ]?(EWR|Bürger)|EU-Mitgliedstaat)\b",
        "Staatsangehörigkeit",
    ),
    (r"\b(citizenship|work\s+permit|right\s+to\s+work)\b", "Staatsangehörigkeit"),
    # Akademischer Abschluss
    (
        r"\b(Hochschul(studium|abschluss)|Universitätsdiplom|Master|Diplom|Bachelor)\b"
        r".*\b(in|of)\b.+",
        "Akademischer Abschluss",
    ),
    (
        r"\b(Bachelor'?s?|Master'?s?|PhD|Doctoral)\s+degree\b",
        "Akademischer Abschluss",
    ),
    # Pauschale Berufserfahrung (X Jahre ohne Tech-Spezifik)
    (
        r"\b(Mindestens\s+\d+|\d+\+?)\s*Jahr(e)?\s+(Berufserfahrung|Erfahrung|practice)\b",
        "Berufserfahrung-pauschal",
    ),
    (
        r"\b\d+\+?\s+years?\s+(of\s+)?(experience|professional)\b",
        "Berufserfahrung-pauschal",
    ),
    # Reise / Mobilität
    (r"\b(Reisebereitschaft|Dienstreis(e|en)|Bereitschaft\s+zu\s+Reisen)\b", "Mobilität"),
    (r"\b(willing(ness)?\s+to\s+travel|travel\s+required)\b", "Mobilität"),
    # Soft Skills DE
    (
        r"\b(Strukturiert(e|er)?\s+(Analyse|Arbeitsweise|Denken)|"
        r"Teamfähigkeit|Kommunikationsstärke|Wertschätzender\s+Umgang|"
        r"Digitale\s+Kompetenzen?|Belastbar(keit)?|Eigenverantwortlich)\b",
        "Soft Skill",
    ),
    # Soft Skills EN
    (
        r"\b(Problem.?solving|Critical\s+thinking|Analytical\s+(thinking|skills)|"
        r"Team\s+(work|player|collaboration)|Communication\s+skills?|"
        r"Self.?starter|Ownership|End.?to.?end\s+ownership|"
        r"Entrepreneurial|Drive|Ambition|Leadership)\b",
        "Soft Skill",
    ),
    # Allgemein (zu generisch um spezifischer Skill zu sein)
    (r"^\s*Software\s+(development|engineering)\s*$", "Allgemein"),
    (r"^\s*(Programming|Coding)\s*$", "Allgemein"),
    # Bereitschaft / Verfügbarkeit
    (r"\bBereitschaft\s+(zur?|für)\b", "Bereitschaft"),
]


def _is_soft_requirement(term: str, kb: KnowledgeBase) -> tuple[bool, str]:
    """Prüft ob ein must_have-String eine formale Voraussetzung ist.

    Rückgabe: (ist_soft_requirement, kategorie). Bei False ist kategorie "".

    Heuristik:
    1. Wenn der String einen klar erkennbaren Knowledge-Tech enthält
       (z.B. "Java oder TypeScript"), ist es KEIN soft-requirement —
       Tech-Anforderungen haben Vorrang.
    2. Sonst: Pattern-Matching gegen Sprache/Sicherheit/Studium/etc.
    """
    # Wenn klare Tech-Anforderung enthalten: nicht als Soft-Req klassifizieren
    if _extract_known_techs(term, kb):
        return False, ""

    for pattern, kategorie in _SOFT_REQUIREMENT_PATTERNS:
        if re.search(pattern, term, re.IGNORECASE):
            return True, kategorie

    return False, ""


def _extract_known_techs(text: str, kb: KnowledgeBase) -> list[str]:
    """Findet alle Knowledge-Technologien deren Name/Alias als ganzes Wort
    im Text vorkommt. Word-Boundary verhindert dass z.B. 'Go' in 'Going' matcht.
    Gender-Varianten (Architekt*in, Architektin) werden vor dem Matching normalisiert.
    Gibt kanonische Tech-Namen zurück (Aliase werden aufgelöst).
    """
    normalized = _normalize_gender(text)
    found: list[str] = []
    for t in kb.technologies:
        candidates = [t.name, *t.aliases]
        for cand in candidates:
            # Wort-Grenzen: Tech-Name darf vorne und hinten nicht von
            # einem alphanumerischen Zeichen umgeben sein
            pattern = r"(?<![A-Za-z0-9])" + re.escape(cand) + r"(?![A-Za-z0-9])"
            if re.search(pattern, normalized, re.IGNORECASE):
                if t.name not in found:
                    found.append(t.name)
                break
    return found


class GapType(StrEnum):
    """Klassen von Lücken nach Schließbarkeit."""

    ARTIKULATION = "Artikulations-Lücke"  # vorhanden, nicht kommuniziert
    ZERTIFIZIERUNG = "Zertifizierungs-Lücke"  # >70% Überlappung mit vorhandenem Wissen
    ERFAHRUNG = "Erfahrungs-Lücke"  # fehlt, mittelfristig erlernbar
    STRUKTURELL = "Strukturelle Lücke"  # fundamental fehlend
    VORAUSSETZUNG = "Voraussetzung"  # formal/rechtlich/sprachlich — Selbst-Check


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
    role_match: list[str] = []  # Knowledge-Terms aus rolle, die im Profil sind
    voraussetzungen: list[tuple[str, str]] = []  # (Original-Term, Kategorie)
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

    # 4. Multi-Token-Fallback: enthält der String mehrere bekannte Techs
    #    (z.B. "Java oder TypeScript")? Wenn ja, klassifizieren wir als
    #    Erfahrungslücke mit Verweis auf die enthaltenen bekannten Begriffe.
    extracted = _extract_known_techs(term, kb)
    if extracted:
        return Gap(
            term=term,
            type=GapType.ERFAHRUNG,
            reason=f"Enthält bekannte Begriffe ({', '.join(extracted)}), aber keiner im Profil",
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


def _term_matches_profile(
    term: str, profile_techs: set[str], profile_text: str, kb: KnowledgeBase
) -> bool:
    """Prüft ob ein Anforderungs-String mit dem Profil matcht.

    Vier Strategien (in dieser Reihenfolge):
    1. Direkt: ist der ganze term-String eine Tech im Profil?
    2. Normalisiert: löst term über Aliase auf eine Knowledge-Tech auf?
    3. Tokenisierung für reale `.req`-Texte ("Java oder TypeScript"):
       Extrahiere alle Knowledge-Tech-Tokens aus dem term-String und prüfe
       ob mindestens eines im Profil als technology vorhanden ist.
    4. Impliziter Profil-Match: ist einer der extrahierten Knowledge-Tokens
       irgendwo im Profil-Text erwähnt (Projekt-Rolle, Schlüsselkompetenz,
       Kurzprofil etc.)? Das deckt Fälle ab in denen "Architekt" als Rolle,
       aber nicht als technology-Eintrag im Profil steht.
    """
    canon = kb.normalize(term) or term
    if canon.lower() in profile_techs:
        return True
    extracted = _extract_known_techs(term, kb)
    if any(tech.lower() in profile_techs for tech in extracted):
        return True
    # Impliziter Match: Knowledge-Term taucht im Profil-Text auf
    for tech in extracted:
        tech_obj = kb.technology_by_name(tech)
        if tech_obj is None:
            continue
        candidates = [tech_obj.name, *tech_obj.aliases]
        for cand in candidates:
            pattern = r"(?<![A-Za-z0-9])" + re.escape(cand.lower()) + r"(?![A-Za-z0-9])"
            if re.search(pattern, profile_text):
                return True
    return False


def evaluate_offer(profil: Profil, anf: Anforderungen, kb: KnowledgeBase) -> AdvisoryResult:
    """Bewertet ein einzelnes Stellenangebot gegen das Profil + Knowledge."""
    profile_techs = _profile_tech_set(profil, kb)
    profile_text = _profile_text_index(profil)

    # Soft-Requirements aus must_have herausfiltern — sie fließen nicht
    # in den technischen Score ein, sondern in voraussetzungen für Selbst-Check.
    voraussetzungen: list[tuple[str, str]] = []
    technical_must: list[str] = []
    for term in anf.must_have:
        is_soft, kategorie = _is_soft_requirement(term, kb)
        if is_soft:
            voraussetzungen.append((term, kategorie))
        else:
            technical_must.append(term)

    matched_must: list[str] = []
    missing_must: list[str] = []
    for term in technical_must:
        if _term_matches_profile(term, profile_techs, profile_text, kb):
            matched_must.append(term)
        else:
            missing_must.append(term)

    matched_nice = [
        term
        for term in anf.nice_to_have
        if _term_matches_profile(term, profile_techs, profile_text, kb)
    ]

    # Rolle als zusätzlichen Match-Indikator auswerten (mit Profil-Text-Fallback)
    role_match: list[str] = []
    if anf.rolle:
        for tech in _extract_known_techs(anf.rolle, kb):
            tech_obj = kb.technology_by_name(tech)
            if (
                tech.lower() in profile_techs
                or tech_obj is not None
                and any(
                    re.search(
                        r"(?<![A-Za-z0-9])" + re.escape(c.lower()) + r"(?![A-Za-z0-9])",
                        profile_text,
                    )
                    for c in [tech_obj.name, *tech_obj.aliases]
                )
            ):
                role_match.append(tech)

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

    # Score-Nenner sind nur die technischen Anforderungen (ohne Voraussetzungen).
    # Wenn das Angebot KEINE technischen must_haves hat (nur Voraussetzungen),
    # gilt der Score als 1.0 modulo Rolle-Match — Robert muss dann nur die
    # Voraussetzungen selbst prüfen.
    total = len(technical_must)
    raw_score = len(matched_must) / total if total > 0 else 1.0
    # Artikulations-Lücken zählen halb mit (vorhanden, nur nicht artikuliert)
    artikulation_count = sum(1 for g in gaps if g.type == GapType.ARTIKULATION)
    effective_score = raw_score + (0.5 * artikulation_count / total if total > 0 else 0)
    # Rolle-Match: jeder Treffer +0.15 (max 0.30) — kompensiert .req-Dateien
    # mit ausschließlich formalen Voraussetzungen im must_have
    effective_score += min(0.30, 0.15 * len(role_match))
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
        role_match=role_match,
        voraussetzungen=voraussetzungen,
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
