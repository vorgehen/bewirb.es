from __future__ import annotations

from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion

from src.data_loader import load_profile, load_requirements
from src.generators.markdown import generate_markdown
from src.graph_builder import build_graph
from src.pim_to_psm import transform

pytestmark = pytest.mark.snapshot

_DATA = Path(__file__).parent.parent.parent.parent / "data" / "example"
EXAMPLE_PROFILE = _DATA / "example.profile"
EXAMPLE_REQ = _DATA / "example_job.req"


@pytest.fixture(scope="module")
def markdown_output() -> str:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    psm = transform(build_graph(profil), anf)
    return generate_markdown(psm, profil, anf)


def test_markdown_snapshot(markdown_output: str, snapshot: SnapshotAssertion) -> None:
    assert markdown_output == snapshot


def test_markdown_has_required_sections(markdown_output: str) -> None:
    assert "## Technologiekompetenz" in markdown_output
    assert "## Projekterfahrung" in markdown_output
    assert "## Ausbildung" in markdown_output
    assert "## Schluessel-Kompetenzen" in markdown_output


def test_markdown_score_reflects_all_must_have(markdown_output: str) -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    from src.matcher import match_profile_to_requirements

    result = match_profile_to_requirements(profil, anf)
    for tech in result.matched_must_have:
        assert tech in markdown_output
