from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from src.data_loader import load_profile
from src.profile_enricher import (
    ProjektVorschlag,
    _build_prompt,
    _escape_dsl_string,
    _format_projekte,
    _format_wissensgebiete,
    _strip_artifacts,
    enrich_projekt,
    generate_kurzprofil,
    update_kurzprofil_in_profile,
    update_projekt_in_profile,
)

pytestmark = pytest.mark.unit

EXAMPLE_PROFILE = Path(__file__).parent.parent.parent / "data" / "example" / "example.profile"


# ─── Prompt-Aufbau ──────────────────────────────────────────────────────────


def test_build_prompt_substitutes_zielgruppe() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    prompt = _build_prompt(profil, "Consultant")
    assert "Consultant" in prompt
    assert "{{zielgruppe}}" not in prompt


def test_build_prompt_default_zielgruppe_standard() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    prompt = _build_prompt(profil, "")
    assert "Standard" in prompt


def test_build_prompt_includes_profile_data() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    prompt = _build_prompt(profil, "Standard")
    # Person-Titel und mindestens ein Wissensgebiet-Titel aus dem Profil
    assert profil.person.title in prompt
    assert any(w.titel in prompt for w in profil.wissensgebiete)


def test_format_projekte_neueste_zuerst() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    text = _format_projekte(profil, n=10)
    # Bei mehr als einem Projekt sollten die Zeilen absteigend nach start sein
    lines = text.splitlines()
    starts = [line.split()[1].split("–")[0] for line in lines if line.startswith("- ")]
    assert starts == sorted(starts, reverse=True)


def test_format_wissensgebiete_nach_reihenfolge() -> None:
    profil = load_profile(EXAMPLE_PROFILE)
    text = _format_wissensgebiete(profil)
    # Die Wissensgebiet-Titel erscheinen in aufsteigender Reihenfolge.
    sorted_titel = [w.titel for w in sorted(profil.wissensgebiete, key=lambda w: w.reihenfolge)]
    positionen = [text.find(t) for t in sorted_titel]
    assert positionen == sorted(positionen)


# ─── Output-Bereinigung ─────────────────────────────────────────────────────


def test_strip_artifacts_entfernt_code_fences() -> None:
    raw = "```\nDas ist der Text.\n```"
    assert _strip_artifacts(raw) == "Das ist der Text."


def test_strip_artifacts_entfernt_anfuehrungszeichen() -> None:
    assert _strip_artifacts('"Das ist der Text."') == "Das ist der Text."


def test_strip_artifacts_laesst_plain_text_unveraendert() -> None:
    assert _strip_artifacts("Das ist der Text.") == "Das ist der Text."


# ─── DSL-Schreiben ─────────────────────────────────────────────────────────


def test_escape_dsl_string_entwertet_quotes_und_backslash() -> None:
    assert _escape_dsl_string('Er sagte: "Hallo"') == 'Er sagte: \\"Hallo\\"'
    assert _escape_dsl_string("Pfad: C:\\users") == "Pfad: C:\\\\users"


def test_update_kurzprofil_in_profile_aktualisiert(tmp_path: Path) -> None:
    src = EXAMPLE_PROFILE.read_text(encoding="utf-8")
    target = tmp_path / "test.profile"
    target.write_text(src, encoding="utf-8")

    neu = "Diplom-Physiker mit 30 Jahren Erfahrung in Architektur und MDD."
    ok = update_kurzprofil_in_profile(target, neu)
    assert ok is True

    written = target.read_text(encoding="utf-8")
    assert neu in written
    # Stelle sicher dass die Datei weiterhin valide ist
    from src.profile_importer import validate_profile_dsl

    validate_profile_dsl(written)


def test_update_kurzprofil_returns_false_when_no_field(tmp_path: Path) -> None:
    """Wenn kein kurzprofil:-Feld existiert, gibt update False zurück."""
    minimal = """
    branche IT { label: "IT" }
    person P {
        title: "Dev"
        contact { email: "x@x.de" }
    }
    """
    target = tmp_path / "min.profile"
    target.write_text(minimal, encoding="utf-8")

    ok = update_kurzprofil_in_profile(target, "Neuer Text")
    assert ok is False


# ─── Orchestrierung (mit Claude-Mock) ──────────────────────────────────────


def test_generate_kurzprofil_calls_claude_and_strips(tmp_path: Path) -> None:
    profil = load_profile(EXAMPLE_PROFILE)

    fake_text = '"Ein Mock-Kurzprofil mit Quotes."'

    class _FakeBlock:
        def __init__(self, text: str) -> None:
            self.text = text

    class _FakeMessage:
        def __init__(self, text: str) -> None:
            self.content = [_FakeBlock(text)]

    fake_message = _FakeMessage(fake_text)

    with patch("src.profile_enricher.anthropic.Anthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create.return_value = fake_message
        # Workaround: isinstance-Check in generate_kurzprofil. Wir patchen TextBlock.
        with patch("src.profile_enricher.TextBlock", _FakeBlock):
            result = generate_kurzprofil(profil, zielgruppe="Standard")

    assert result == "Ein Mock-Kurzprofil mit Quotes."
    instance.messages.create.assert_called_once()


# ─── Mode projekt ──────────────────────────────────────────────────────────


def test_enrich_projekt_parses_json_response() -> None:
    profil = load_profile(EXAMPLE_PROFILE)

    fake_text = (
        '{"description": "Migration auf Microservices-Architektur mit Java/Spring.", '
        '"achievements": ["Latenz um 40% reduziert", "Deployment-Frequenz verzehnfacht"]}'
    )

    class _FakeBlock:
        def __init__(self, text: str) -> None:
            self.text = text

    class _FakeMessage:
        def __init__(self, text: str) -> None:
            self.content = [_FakeBlock(text)]

    with patch("src.profile_enricher.anthropic.Anthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create.return_value = _FakeMessage(fake_text)
        with patch("src.profile_enricher.TextBlock", _FakeBlock):
            result = enrich_projekt(profil, "Projekt_A", "Anonymisiertes Extrakt …")

    assert isinstance(result, ProjektVorschlag)
    assert "Microservices" in result.description
    assert "Latenz um 40% reduziert" in result.achievements
    assert len(result.achievements) == 2


def test_enrich_projekt_unknown_id_raises() -> None:
    profil = load_profile(EXAMPLE_PROFILE)

    class _FakeBlock:
        def __init__(self, text: str) -> None:
            self.text = text

    class _FakeMessage:
        def __init__(self, text: str) -> None:
            self.content = [_FakeBlock(text)]

    with patch("src.profile_enricher.anthropic.Anthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create.return_value = _FakeMessage('{"description":"x"}')
        with (
            patch("src.profile_enricher.TextBlock", _FakeBlock),
            pytest.raises(KeyError),
        ):
            enrich_projekt(profil, "NICHT_VORHANDEN", "Extrakt")


def test_update_projekt_in_profile_aktualisiert_description_und_achievements(
    tmp_path: Path,
) -> None:
    src = EXAMPLE_PROFILE.read_text(encoding="utf-8")
    target = tmp_path / "test.profile"
    target.write_text(src, encoding="utf-8")

    vorschlag = ProjektVorschlag(
        description="Neue verbesserte Beschreibung.",
        achievements=["Konkretes Achievement A", "Konkretes Achievement B"],
    )
    ok = update_projekt_in_profile(target, "Projekt_A", vorschlag)
    assert ok is True

    # Profil ist weiterhin valide
    from src.profile_importer import validate_profile_dsl

    written = target.read_text(encoding="utf-8")
    validate_profile_dsl(written)

    # Inhalte wurden geschrieben
    p_after = load_profile(target)
    p_a = next(p for p in p_after.projekte if p.name == "Projekt_A")
    assert p_a.description == "Neue verbesserte Beschreibung."
    assert "Konkretes Achievement A" in p_a.achievements
    assert "Konkretes Achievement B" in p_a.achievements


def test_update_projekt_unknown_id_returns_false(tmp_path: Path) -> None:
    src = EXAMPLE_PROFILE.read_text(encoding="utf-8")
    target = tmp_path / "test.profile"
    target.write_text(src, encoding="utf-8")

    vorschlag = ProjektVorschlag(description="x")
    ok = update_projekt_in_profile(target, "NICHT_VORHANDEN", vorschlag)
    assert ok is False


def test_update_projekt_leerer_vorschlag_returns_false(tmp_path: Path) -> None:
    src = EXAMPLE_PROFILE.read_text(encoding="utf-8")
    target = tmp_path / "test.profile"
    target.write_text(src, encoding="utf-8")

    vorschlag = ProjektVorschlag(description="", achievements=[])
    ok = update_projekt_in_profile(target, "Projekt_A", vorschlag)
    assert ok is False
    # Datei unverändert
    assert target.read_text(encoding="utf-8") == src


@pytest.mark.integration
def test_integration_real_kurzprofil_for_example(tmp_path: Path) -> None:
    """End-to-End: echter Claude-Aufruf gegen example.profile."""
    import os

    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY nicht gesetzt")

    profil = load_profile(EXAMPLE_PROFILE)
    result = generate_kurzprofil(profil, zielgruppe="Consultant")
    assert isinstance(result, str)
    assert 50 < len(result) < 800  # plausible Länge
