from __future__ import annotations

from pathlib import Path

import pytest

from src.data_loader import load_profile, load_requirements
from src.graph_builder import build_graph
from src.pim_to_psm import transform

pytestmark = pytest.mark.unit

EXAMPLE_PROFILE = Path(__file__).parent.parent.parent / "data" / "example" / "example.profile"
EXAMPLE_REQ = Path(__file__).parent.parent.parent / "data" / "example" / "example_job.req"


def test_transform_returns_graph() -> None:
    import networkx as nx

    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    assert isinstance(psm, nx.DiGraph)


def test_psm_has_person_node() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    person_nodes = [n for n, d in psm.nodes(data=True) if d.get("type") == "Person"]
    assert len(person_nodes) == 1


def test_psm_annotates_matched_technologies() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    tech_nodes = [d for _, d in psm.nodes(data=True) if d.get("type") == "Technologiekompetenz"]
    # At least one tech node should be annotated as matched
    assert any(d.get("matched") for d in tech_nodes)


def test_psm_preserves_all_nodes() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    assert psm.number_of_nodes() == g.number_of_nodes()
