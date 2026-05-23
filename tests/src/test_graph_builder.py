from __future__ import annotations

from pathlib import Path

import pytest

from src.data_loader import load_profile
from src.graph_builder import build_graph

pytestmark = pytest.mark.unit

EXAMPLE_PROFILE = Path(__file__).parent.parent.parent / "data" / "example" / "example.profile"


def test_graph_has_nodes() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    g = build_graph(profil)
    assert g.number_of_nodes() > 0


def test_graph_has_person_node() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    g = build_graph(profil)
    person_nodes = [n for n, d in g.nodes(data=True) if d.get("type") == "Person"]
    assert len(person_nodes) == 1


def test_graph_has_projekt_nodes() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    g = build_graph(profil)
    projekt_nodes = [n for n, d in g.nodes(data=True) if d.get("type") == "Projekterfahrung"]
    assert len(projekt_nodes) >= 1


def test_graph_has_technologie_nodes() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    g = build_graph(profil)
    tech_nodes = [n for n, d in g.nodes(data=True) if d.get("type") == "Technologiekompetenz"]
    assert len(tech_nodes) >= 1


def test_graph_projekt_uses_technologie_edge() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    g = build_graph(profil)
    uses_edges = [(u, v) for u, v, d in g.edges(data=True) if d.get("rel") == "uses"]
    assert len(uses_edges) >= 1


def test_graph_person_hat_projekt_edge() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    g = build_graph(profil)
    hat_edges = [(u, v) for u, v, d in g.edges(data=True) if d.get("rel") == "hat_projekt"]
    assert len(hat_edges) >= 1
