from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from anthropic.types import TextBlock

from src.extractor import _parse_json, extract_requirements

pytestmark = pytest.mark.unit

SAMPLE_JSON = """
{
  "rolle": "Python Entwickler",
  "branchen": ["E-Commerce"],
  "must_have": ["Python", "Django"],
  "nice_to_have": ["Celery"],
  "keywords": ["Backend", "REST"],
  "context": "Webshop-Plattform auf Python-Basis"
}
"""

SAMPLE_AUSSCHREIBUNG = """
Wir suchen einen erfahrenen Python Entwickler (m/w/d) für unsere E-Commerce-Plattform.
Zwingend erforderlich: Python, Django.
Von Vorteil: Celery.
"""


def test_parse_json_extracts_object() -> None:
    result = _parse_json(SAMPLE_JSON)
    assert result["rolle"] == "Python Entwickler"
    must_have = result["must_have"]
    assert isinstance(must_have, list)
    assert "Python" in must_have


def test_parse_json_handles_surrounding_text() -> None:
    text = f"Hier ist das Ergebnis:\n{SAMPLE_JSON}\nDas war alles."
    result = _parse_json(text)
    assert result["rolle"] == "Python Entwickler"


def test_extract_requirements_returns_anforderungen() -> None:
    mock_message = MagicMock()
    mock_message.content = [TextBlock(type="text", text=SAMPLE_JSON)]

    with patch("src.extractor.anthropic.Anthropic") as mock_client_cls:
        mock_client_cls.return_value.messages.create.return_value = mock_message
        anf = extract_requirements(SAMPLE_AUSSCHREIBUNG, name="Test_Job")

    assert anf.rolle == "Python Entwickler"
    assert "Python" in anf.must_have
    assert "Django" in anf.must_have
    assert "Celery" in anf.nice_to_have
    assert anf.name == "Test_Job"


def test_extract_requirements_uses_haiku_model() -> None:
    mock_message = MagicMock()
    mock_message.content = [TextBlock(type="text", text=SAMPLE_JSON)]

    with patch("src.extractor.anthropic.Anthropic") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.messages.create.return_value = mock_message
        extract_requirements(SAMPLE_AUSSCHREIBUNG)
        call_kwargs = mock_instance.messages.create.call_args[1]
        assert "haiku" in call_kwargs["model"]


def test_extract_and_write_req_creates_file(tmp_path: Path) -> None:
    from src.extractor import extract_and_write_req

    mock_message = MagicMock()
    mock_message.content = [TextBlock(type="text", text=SAMPLE_JSON)]
    out = tmp_path / "test.req"

    with patch("src.extractor.anthropic.Anthropic") as mock_client_cls:
        mock_client_cls.return_value.messages.create.return_value = mock_message
        extract_and_write_req(SAMPLE_AUSSCHREIBUNG, out, name="Test_Job")

    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "requirements Test_Job" in content
    assert '"Python Entwickler"' in content
    assert '"Python"' in content


@pytest.mark.integration
def test_extract_requirements_real_api() -> None:
    """Echter API-Call — benoetigt ANTHROPIC_API_KEY."""
    ausschreibung = """
    Wir suchen einen Senior Java Entwickler (m/w/d).
    Pflichtanforderungen: Java 17+, Spring Boot, REST APIs.
    Wuenschenswert: Kubernetes, Docker.
    Branche: Finanzsektor.
    """
    anf = extract_requirements(ausschreibung, name="Integration_Test")
    assert anf.rolle != ""
    assert len(anf.must_have) >= 1
    assert "Java" in " ".join(anf.must_have)
