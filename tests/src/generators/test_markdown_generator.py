from __future__ import annotations

from pathlib import Path

import pytest

from src.data_loader import load_profile, load_requirements
from src.generators.markdown import generate_markdown
from src.graph_builder import build_graph
from src.pim_to_psm import transform

pytestmark = pytest.mark.unit

_DATA = Path(__file__).parent.parent.parent.parent / "data" / "example"
EXAMPLE_PROFILE = _DATA / "example.profile"
EXAMPLE_REQ = _DATA / "example_job.req"


def test_generate_markdown_returns_string() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    md = generate_markdown(psm, profil, anf)
    assert isinstance(md, str)
    assert len(md) > 0


def test_markdown_contains_rolle() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    md = generate_markdown(psm, profil, anf)
    assert anf.rolle in md


def test_markdown_contains_person_title() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    md = generate_markdown(psm, profil, anf)
    assert profil.person.title in md


def test_markdown_contains_projekt_section() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    md = generate_markdown(psm, profil, anf)
    assert "## Projekterfahrung" in md or "Projekterfahrung" in md


def test_markdown_contains_technologie_section() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    md = generate_markdown(psm, profil, anf)
    assert "Technologie" in md or "Kompetenz" in md


def test_markdown_written_to_file(tmp_path: Path) -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    md = generate_markdown(psm, profil, anf)
    out = tmp_path / "profil.md"
    out.write_text(md, encoding="utf-8")
    assert out.exists()
    assert out.stat().st_size > 0
