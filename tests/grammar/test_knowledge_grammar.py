from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from textx import metamodel_from_file
from textx.exceptions import TextXSemanticError, TextXSyntaxError

pytestmark = pytest.mark.unit

GRAMMAR = Path(__file__).parent.parent.parent / "grammar" / "knowledge.tx"
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "knowledge"


@pytest.fixture(scope="module")
def knowledge_mm() -> Any:
    return metamodel_from_file(str(GRAMMAR))


# ─── Smoke tests: alle bestehenden Inhalte parsen ───────────────────────────


def test_taxonomy_knowledge_parses(knowledge_mm: Any) -> None:
    model = knowledge_mm.model_from_file(str(KNOWLEDGE_DIR / "taxonomy.knowledge"))
    techs = [e for e in model.elements if e.__class__.__name__ == "Technology"]
    rels = [e for e in model.elements if e.__class__.__name__ == "TechnologyRelation"]
    assert len(techs) >= 20, "Taxonomie sollte mindestens 20 Technologien enthalten"
    assert len(rels) >= 5, "Kompetenzgraph sollte mindestens 5 Relationen enthalten"


def test_opinions_knowledge_parses(knowledge_mm: Any) -> None:
    model = knowledge_mm.model_from_file(str(KNOWLEDGE_DIR / "opinions.knowledge"))
    prefs = [e for e in model.elements if e.__class__.__name__ == "Preference"]
    warns = [e for e in model.elements if e.__class__.__name__ == "WarnRule"]
    boosts = [e for e in model.elements if e.__class__.__name__ == "BoostRule"]
    assert len(prefs) >= 3, "Mindestens 3 Preferences erwartet"
    assert len(warns) >= 1
    assert len(boosts) >= 1


def test_all_role_profiles_parse(knowledge_mm: Any) -> None:
    roles_dir = KNOWLEDGE_DIR / "roles"
    role_files = sorted(roles_dir.glob("*.knowledge"))
    assert len(role_files) >= 3, "Mindestens 3 Rollenprofile erwartet"
    for f in role_files:
        model = knowledge_mm.model_from_file(str(f))
        roles = [e for e in model.elements if e.__class__.__name__ == "RoleProfile"]
        assert len(roles) == 1, f"{f.name}: genau ein RoleProfile pro Datei erwartet"


# ─── Strukturelle Eigenschaften ─────────────────────────────────────────────


def test_kubernetes_normalisiert_auf_container_orchestration(knowledge_mm: Any) -> None:
    """Verifikationskriterium Phase 7.5: 'Kubernetes' -> 'Container Orchestration'."""
    model = knowledge_mm.model_from_file(str(KNOWLEDGE_DIR / "taxonomy.knowledge"))
    techs = {t.name: t for t in model.elements if t.__class__.__name__ == "Technology"}
    assert "Kubernetes" in techs
    k8s = techs["Kubernetes"]
    assert k8s.category == "Container Orchestration"
    assert "Container Orchestration" in k8s.aliases or "K8s" in k8s.aliases


def test_technology_relation_resolves_source(knowledge_mm: Any) -> None:
    """Cross-Reference: TechnologyRelation.source verweist auf Technology-Knoten."""
    model = knowledge_mm.model_from_file(str(KNOWLEDGE_DIR / "taxonomy.knowledge"))
    relations = [e for e in model.elements if e.__class__.__name__ == "TechnologyRelation"]
    assert len(relations) > 0
    for r in relations:
        assert r.source is not None
        assert r.source.__class__.__name__ == "Technology"
        assert isinstance(r.targets, list)


def test_role_profile_has_competencies(knowledge_mm: Any) -> None:
    model = knowledge_mm.model_from_file(
        str(KNOWLEDGE_DIR / "roles" / "software_engineer.knowledge")
    )
    role = next(e for e in model.elements if e.__class__.__name__ == "RoleProfile")
    assert role.title == "Software Engineer"
    assert role.sfia_level >= 3
    assert len(role.competencies) >= 1


# ─── Syntax-Fehler werden erkannt ───────────────────────────────────────────


def test_invalid_relation_type_rejected(knowledge_mm: Any, tmp_path: Path) -> None:
    content = """
    technology Java { category: "Programmiersprachen" }
    relation r1 {
        source: Java
        kind: foobar
        targets: ["X"]
    }
    """
    f = tmp_path / "bad.knowledge"
    f.write_text(content, encoding="utf-8")
    with pytest.raises(TextXSyntaxError):
        knowledge_mm.model_from_file(str(f))


def test_unknown_technology_in_relation_rejected(knowledge_mm: Any, tmp_path: Path) -> None:
    """Cross-Reference-Validierung: source muss eine deklarierte Technology sein."""
    content = """
    technology Java { category: "Programmiersprachen" }
    relation r1 {
        source: Kotlin
        kind: ueberschneidet_sich_mit
        targets: ["Java"]
    }
    """
    f = tmp_path / "bad.knowledge"
    f.write_text(content, encoding="utf-8")
    with pytest.raises((TextXSyntaxError, TextXSemanticError)):
        knowledge_mm.model_from_file(str(f))


def test_invalid_competency_area_rejected(knowledge_mm: Any, tmp_path: Path) -> None:
    content = """
    role r {
        title: "X"
        sfia_level: 4
        description: "Test"
        unbekanntegebiet {
            erwartet: ["Java"]
        }
    }
    """
    f = tmp_path / "bad.knowledge"
    f.write_text(content, encoding="utf-8")
    with pytest.raises(TextXSyntaxError):
        knowledge_mm.model_from_file(str(f))
