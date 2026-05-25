from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx
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


# ─── Phase 8c: Zielgruppen-Logik ────────────────────────────────────────────


def _person_data(psm: nx.DiGraph) -> dict[str, Any]:
    for _, data in psm.nodes(data=True):
        if data.get("type") == "Person":
            return dict(data)
    raise AssertionError("Keine Person im PSM")


def test_psm_person_hat_schluesselkompetenzen_ordered() -> None:
    """example.profile hat schluesselkompetenzen → PSM hat _ordered Annotation."""
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    p = _person_data(psm)
    ordered = p.get("schluesselkompetenzen_ordered")
    assert ordered is not None
    assert len(ordered) >= 1
    # Jeder Eintrag hat key, label, items
    for entry in ordered:
        assert "key" in entry and "label" in entry and "items" in entry
        assert len(entry["items"]) > 0


def test_psm_reihenfolge_haengt_von_zielgruppe_ab(tmp_path: Path) -> None:
    """Mit zielgruppe=StartUp steht technologie an erster Stelle, mit Behoerde nicht."""
    profil = load_profile(EXAMPLE_PROFILE)
    g = build_graph(profil)

    def req_mit_zielgruppe(stil: str) -> Path:
        content = f"""
        requirements Test {{
            rolle: "Test"
            zielgruppe: {stil}
            must_have: ["Java"]
        }}
        """
        f = tmp_path / f"{stil}.req"
        f.write_text(content, encoding="utf-8")
        return f

    psm_startup = transform(g, load_requirements(req_mit_zielgruppe("StartUp")))
    psm_behoerde = transform(g, load_requirements(req_mit_zielgruppe("Behoerde")))

    startup_first = _person_data(psm_startup)["schluesselkompetenzen_ordered"][0]
    behoerde_first = _person_data(psm_behoerde)["schluesselkompetenzen_ordered"][0]

    assert startup_first["key"] == "technologie"
    assert startup_first["label"] == "Tech Stack"
    assert behoerde_first["key"] == "fachkompetenz"


def test_psm_ohne_schluesselkompetenzen_keine_annotation(tmp_path: Path) -> None:
    """Profil ohne schluesselkompetenzen → keine _ordered Annotation."""
    minimal_profile = """
    branche IT { label: "IT" }
    auftraggeber X { label: "X" }
    technology Java { category: Programmiersprache proficiency: Experte years: 5 }
    person P { title: "Dev" contact { email: "x@x.de" } }
    """
    f = tmp_path / "min.profile"
    f.write_text(minimal_profile, encoding="utf-8")

    profil = load_profile(f)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    p = _person_data(psm)
    assert "schluesselkompetenzen_ordered" not in p


def test_psm_leere_kategorien_werden_uebersprungen(tmp_path: Path) -> None:
    """Kategorien ohne Inhalt erscheinen nicht in _ordered."""
    profile_text = """
    branche IT { label: "IT" }
    auftraggeber X { label: "X" }
    technology Java { category: Programmiersprache proficiency: Experte years: 5 }
    person P { title: "Dev" contact { email: "x@x.de" } }
    schluesselkompetenzen {
        technologie: ["Java", "Spring"]
        fuehrungkompetenz: ["Mentoring"]
    }
    """
    f = tmp_path / "p.profile"
    f.write_text(profile_text, encoding="utf-8")

    profil = load_profile(f)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    p = _person_data(psm)
    ordered = p["schluesselkompetenzen_ordered"]
    keys = {entry["key"] for entry in ordered}
    assert keys == {"technologie", "fuehrungkompetenz"}
