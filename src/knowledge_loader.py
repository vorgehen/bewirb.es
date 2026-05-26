"""Lädt den Knowledge Layer (knowledge/*.knowledge) als typisierte Python-Strukturen.

Die `.knowledge`-Dateien sind TextX-konform zur Grammatik `grammar/knowledge.tx`.
Der Loader parst sie und gibt sie als pydantic-validierte Knowledge-Klassen
zurück.

Verwendung in Phase 8a Advisory; entkoppelt von src.matcher und src.advisor.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel
from textx import metamodel_from_file

GRAMMAR_FILE = Path(__file__).parent.parent / "grammar" / "knowledge.tx"
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


class Technology(BaseModel):
    name: str
    category: str = ""
    aliases: list[str] = []
    # sfia_levels: dict[years, level] — sortiert
    sfia_curve: list[tuple[int, int]] = []


class TechnologyRelation(BaseModel):
    name: str
    source: str  # Technology-Name
    kind: str  # benoetigt | ueberschneidet_sich_mit | erweitert | impliziert
    targets: list[str] = []


class RoleProfile(BaseModel):
    name: str
    title: str = ""
    sfia_level: int = 0
    description: str = ""
    # competencies: area -> dict mit erwartet/wuenschenswert
    competencies: dict[str, dict[str, list[str]]] = {}


class Opinions(BaseModel):
    preferences: list[dict[str, str]] = []
    warn_rules: list[dict[str, list[str] | str]] = []
    boost_rules: list[dict[str, list[str] | str]] = []
    deprioritize_rules: list[dict[str, list[str] | str]] = []


class KnowledgeBase(BaseModel):
    technologies: list[Technology] = []
    relations: list[TechnologyRelation] = []
    roles: list[RoleProfile] = []
    opinions: Opinions = Opinions()

    def technology_by_name(self, name: str) -> Technology | None:
        """Exakter Lookup."""
        for t in self.technologies:
            if t.name == name:
                return t
        return None

    def normalize(self, term: str) -> str | None:
        """Sucht den kanonischen Technology-Namen anhand Name oder Alias.

        Case-insensitive. Gibt None zurück wenn nichts gefunden.
        """
        term_lower = term.lower()
        for t in self.technologies:
            if t.name.lower() == term_lower:
                return t.name
            for alias in t.aliases:
                if alias.lower() == term_lower:
                    return t.name
        return None

    def role_by_name(self, name: str) -> RoleProfile | None:
        for r in self.roles:
            if r.name == name or r.title == name:
                return r
        return None


# ─── Loader ─────────────────────────────────────────────────────────────────


def _load_knowledge_file(mm: object, path: Path) -> list[object]:
    """Parst eine .knowledge-Datei und gibt die Element-Liste zurück."""
    model = mm.model_from_file(str(path))  # type: ignore[attr-defined]
    return list(model.elements)


def _to_technology(obj: object) -> Technology:
    sfia_curve = []
    for lvl_obj in getattr(obj, "sfia_levels", []) or []:
        sfia_curve.append((int(lvl_obj.years), int(lvl_obj.level)))
    return Technology(
        name=getattr(obj, "name", ""),
        category=getattr(obj, "category", "") or "",
        aliases=list(getattr(obj, "aliases", []) or []),
        sfia_curve=sorted(sfia_curve),
    )


def _to_relation(obj: object) -> TechnologyRelation:
    src_obj = getattr(obj, "source", None)
    src_name = getattr(src_obj, "name", "") if src_obj else ""
    return TechnologyRelation(
        name=getattr(obj, "name", ""),
        source=src_name,
        kind=getattr(obj, "kind", "") or "",
        targets=list(getattr(obj, "targets", []) or []),
    )


def _to_role(obj: object) -> RoleProfile:
    competencies: dict[str, dict[str, list[str]]] = {}
    for c_obj in getattr(obj, "competencies", []) or []:
        area = getattr(c_obj, "area", "")
        competencies[area] = {
            "erwartet": list(getattr(c_obj, "erwartet", []) or []),
            "wuenschenswert": list(getattr(c_obj, "wuenschenswert", []) or []),
        }
    return RoleProfile(
        name=getattr(obj, "name", ""),
        title=getattr(obj, "title", "") or "",
        sfia_level=int(getattr(obj, "sfia_level", 0) or 0),
        description=getattr(obj, "description", "") or "",
        competencies=competencies,
    )


def _to_opinion_entry(obj: object) -> dict[str, list[str] | str]:
    """Generic: Felder name/indicators/reason/topic/prefer/over abgreifen."""
    result: dict[str, list[str] | str] = {}
    for field in ("name", "topic", "prefer", "over", "reason"):
        v = getattr(obj, field, None)
        if v:
            result[field] = str(v)
    inds = getattr(obj, "indicators", None)
    if inds:
        result["indicators"] = list(inds)
    return result


def load_knowledge_base(knowledge_dir: Path = KNOWLEDGE_DIR) -> KnowledgeBase:
    """Lädt alle .knowledge-Dateien rekursiv aus dem Verzeichnis."""
    if not knowledge_dir.exists():
        return KnowledgeBase()

    mm = metamodel_from_file(str(GRAMMAR_FILE))

    technologies: list[Technology] = []
    relations: list[TechnologyRelation] = []
    roles: list[RoleProfile] = []
    preferences: list[dict[str, str]] = []
    warn_rules: list[dict[str, list[str] | str]] = []
    boost_rules: list[dict[str, list[str] | str]] = []
    deprioritize_rules: list[dict[str, list[str] | str]] = []

    for path in sorted(knowledge_dir.rglob("*.knowledge")):
        for elem in _load_knowledge_file(mm, path):
            cls = elem.__class__.__name__
            if cls == "Technology":
                technologies.append(_to_technology(elem))
            elif cls == "TechnologyRelation":
                relations.append(_to_relation(elem))
            elif cls == "RoleProfile":
                roles.append(_to_role(elem))
            elif cls == "Preference":
                entry = _to_opinion_entry(elem)
                # Preference enthält nur strings — Cast zur Typ-Konsistenz
                preferences.append({k: str(v) for k, v in entry.items() if isinstance(v, str)})
            elif cls == "WarnRule":
                warn_rules.append(_to_opinion_entry(elem))
            elif cls == "BoostRule":
                boost_rules.append(_to_opinion_entry(elem))
            elif cls == "DeprioritizeRule":
                deprioritize_rules.append(_to_opinion_entry(elem))

    return KnowledgeBase(
        technologies=technologies,
        relations=relations,
        roles=roles,
        opinions=Opinions(
            preferences=preferences,
            warn_rules=warn_rules,
            boost_rules=boost_rules,
            deprioritize_rules=deprioritize_rules,
        ),
    )
