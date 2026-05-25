from __future__ import annotations

from pathlib import Path

import pytest

from src.data_loader import Anforderungen, load_profile, load_requirements
from src.generators.word import _build_context, create_default_template, generate_word_file
from src.graph_builder import build_graph
from src.pim_to_psm import transform

pytestmark = pytest.mark.unit

_DATA = Path(__file__).parent.parent.parent.parent / "data" / "example"
EXAMPLE_PROFILE = _DATA / "example.profile"
EXAMPLE_REQ = _DATA / "example_job.req"


@pytest.fixture(scope="module")
def template_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("templates") / "profil.docx"
    create_default_template(path)
    return path


def test_create_default_template_creates_file(tmp_path: Path) -> None:
    tmpl = tmp_path / "test_template.docx"
    create_default_template(tmpl)
    assert tmpl.exists()
    assert tmpl.stat().st_size > 0


def test_build_context_has_required_keys() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    ctx = _build_context(psm, profil, anf)
    expected = (
        "person_title",
        "technologien",
        "projekte",
        "ausbildungen",
        "schluesselkompetenzen_kategorien",
        "werdegang",
        "zertifikate",
        "sprachen",
        "persoenliche_daten",
        "kurzprofil",
        "contact_email",
        "zielrolle",
    )
    for key in expected:
        assert key in ctx


def test_build_context_kurzprofil_aus_profil() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    ctx = _build_context(psm, profil, anf)
    assert ctx["kurzprofil"] != ""


def test_build_context_schluesselkompetenzen_kategorien_geordnet() -> None:
    """Aus example.profile + leerer Zielgruppe → Standard-Reihenfolge."""
    profil = load_profile(EXAMPLE_PROFILE)
    anf = Anforderungen()
    g = build_graph(profil)
    psm = transform(g, anf)
    ctx = _build_context(psm, profil, anf)
    kats = ctx["schluesselkompetenzen_kategorien"]
    assert len(kats) >= 1
    for kat in kats:
        assert "key" in kat and "label" in kat and "items" in kat and "items_str" in kat
        assert kat["items_str"]  # nicht leer


def test_build_context_werdegang_und_zertifikate() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    ctx = _build_context(psm, profil, anf)
    assert len(ctx["werdegang"]) >= 1
    assert len(ctx["zertifikate"]) >= 1
    assert len(ctx["sprachen"]) >= 2


def test_build_context_persoenliche_daten_label_value() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    ctx = _build_context(psm, profil, anf)
    pd = ctx["persoenliche_daten"]
    assert pd is not None
    assert "label" in pd and "value" in pd


def test_build_context_technologien_sorted_by_years() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = Anforderungen()
    g = build_graph(profil)
    psm = transform(g, anf)
    ctx = _build_context(psm, profil, anf)
    years = [int(t["years"]) for t in ctx["technologien"]]
    assert years == sorted(years, reverse=True)


def test_build_context_projekte_have_required_fields() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = Anforderungen()
    g = build_graph(profil)
    psm = transform(g, anf)
    ctx = _build_context(psm, profil, anf)
    for p in ctx["projekte"]:
        assert "title" in p
        assert "start" in p
        assert "end" in p
        assert "rolle" in p
        assert "achievements_str" in p


def test_generate_word_creates_docx(tmp_path: Path, template_path: Path) -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = load_requirements(EXAMPLE_REQ)
    g = build_graph(profil)
    psm = transform(g, anf)
    out = tmp_path / "profil_test.docx"
    generate_word_file(psm, profil, anf, out, template=template_path)
    assert out.exists()
    assert out.stat().st_size > 0


def test_generate_word_generic_no_req(tmp_path: Path, template_path: Path) -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    anf = Anforderungen()
    g = build_graph(profil)
    psm = transform(g, anf)
    out = tmp_path / "profil_generic.docx"
    generate_word_file(psm, profil, anf, out, template=template_path)
    assert out.exists()
    assert out.stat().st_size > 0
