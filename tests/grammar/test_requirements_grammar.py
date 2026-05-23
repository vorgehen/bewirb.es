from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from textx.exceptions import TextXSyntaxError

pytestmark = pytest.mark.unit

EXAMPLE_REQ = Path(__file__).parent.parent.parent / "data" / "example" / "example_job.req"


def test_valid_full_requirements(requirements_mm: Any, tmp_path: Path) -> None:
    content = """
    requirements Job_2026 {
        rolle: "Java Entwickler"
        branchen: ["Finanzsektor"]
        must_have: ["Java", "Spring"]
        nice_to_have: ["Kotlin"]
        keywords: ["Backend"]
        context: "Backend-Entwicklung im Finanzbereich"
        expires: 2026-12-31
    }
    """
    f = tmp_path / "test.req"
    f.write_text(content, encoding="utf-8")
    model = requirements_mm.model_from_file(str(f))
    assert model is not None
    assert model.rolle == "Java Entwickler"


def test_minimal_requirements_only_rolle(requirements_mm: Any, tmp_path: Path) -> None:
    content = """
    requirements Minimal {
        rolle: "Entwickler"
    }
    """
    f = tmp_path / "min.req"
    f.write_text(content, encoding="utf-8")
    model = requirements_mm.model_from_file(str(f))
    assert model.rolle == "Entwickler"
    assert model.must_have == []
    assert model.nice_to_have == []


def test_must_have_and_nice_to_have(mini_req: Any) -> None:
    assert "Python" in mini_req.must_have
    assert "Django" in mini_req.nice_to_have
    assert mini_req.rolle == "Python Entwickler"


def test_expires_date_format(mini_req: Any) -> None:
    assert mini_req.expires == "2026-12-31"


def test_example_req_parses(requirements_mm: Any) -> None:
    model = requirements_mm.model_from_file(str(EXAMPLE_REQ))
    assert model is not None
    assert model.rolle != ""
    assert len(model.must_have) > 0


def test_invalid_date_format_rejected(requirements_mm: Any, tmp_path: Path) -> None:
    content = """
    requirements Bad {
        rolle: "Entwickler"
        expires: 26-12-31
    }
    """
    f = tmp_path / "bad.req"
    f.write_text(content, encoding="utf-8")
    with pytest.raises(TextXSyntaxError):
        requirements_mm.model_from_file(str(f))
