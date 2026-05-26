from __future__ import annotations

from pathlib import Path

import pytest

from src.knowledge_loader import KnowledgeBase, load_knowledge_base

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def kb() -> KnowledgeBase:
    return load_knowledge_base()


def test_loads_real_knowledge_dir(kb: KnowledgeBase) -> None:
    assert len(kb.technologies) > 20
    assert len(kb.roles) >= 3
    assert len(kb.opinions.preferences) >= 3


def test_normalize_resolves_aliases(kb: KnowledgeBase) -> None:
    """K8s → Kubernetes, JVM → Java sind in der Taxonomie als Aliase definiert."""
    assert kb.normalize("K8s") == "Kubernetes"
    assert kb.normalize("kubernetes") == "Kubernetes"  # case-insensitive
    assert kb.normalize("JVM") == "Java"


def test_normalize_passes_through_canonical_names(kb: KnowledgeBase) -> None:
    assert kb.normalize("Java") == "Java"


def test_normalize_returns_none_for_unknown(kb: KnowledgeBase) -> None:
    assert kb.normalize("NotARealTechnology_xyz") is None


def test_technology_by_name_exact(kb: KnowledgeBase) -> None:
    tech = kb.technology_by_name("Kubernetes")
    assert tech is not None
    assert tech.category == "Container Orchestration"


def test_role_by_title(kb: KnowledgeBase) -> None:
    r = kb.role_by_name("Software Engineer")
    assert r is not None
    assert r.sfia_level >= 3


def test_relations_loaded_with_source_resolved(kb: KnowledgeBase) -> None:
    assert len(kb.relations) > 0
    for rel in kb.relations:
        # source ist der Name einer Technology
        assert rel.source != ""
        assert rel.kind in (
            "benoetigt",
            "ueberschneidet_sich_mit",
            "erweitert",
            "impliziert",
        )


def test_opinions_warn_and_boost_present(kb: KnowledgeBase) -> None:
    assert len(kb.opinions.warn_rules) >= 1
    assert len(kb.opinions.boost_rules) >= 1
    # Indicator-Feld immer als Liste
    for rule in kb.opinions.warn_rules + kb.opinions.boost_rules:
        assert "indicators" in rule
        assert isinstance(rule["indicators"], list)


def test_load_empty_dir_returns_empty_base(tmp_path: Path) -> None:
    empty = tmp_path / "doesnt_exist"
    kb_empty = load_knowledge_base(empty)
    assert kb_empty.technologies == []
    assert kb_empty.relations == []
    assert kb_empty.roles == []
