from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from textx import metamodel_from_file

GRAMMAR_DIR = Path(__file__).parent.parent / "grammar"

MINI_PROFILE = """
branche IT {
    label: "Informationstechnologie"
}
auftraggeber TestGmbH {
    label: "Test GmbH"
    location: "Berlin"
}
technology Python {
    category: Programmiersprache
    proficiency: Experte
    years: 5
    keywords: ["Python", "pytest"]
}
person TestNutzer {
    title: "Software Entwickler"
    contact {
        email: "test@beispiel.de"
    }
}
projekt TestProjekt {
    title: "Ein Testprojekt"
    auftraggeber: TestGmbH
    branche: IT
    periode: 2023-01 to today
    rolle: "Entwickler"
    uses: [Python]
    keywords: ["Test"]
}
"""

MINI_REQ = """
requirements Test_Job_2026 {
    rolle: "Python Entwickler"
    must_have: ["Python"]
    nice_to_have: ["Django"]
    keywords: ["Backend"]
    context: "Webentwicklung mit Python"
    expires: 2026-12-31
}
"""


@pytest.fixture(scope="session")
def profile_mm() -> Any:
    return metamodel_from_file(str(GRAMMAR_DIR / "profile.tx"))


@pytest.fixture(scope="session")
def requirements_mm() -> Any:
    return metamodel_from_file(str(GRAMMAR_DIR / "requirements.tx"))


@pytest.fixture
def mini_profile(profile_mm: Any, tmp_path: Path) -> Any:
    f = tmp_path / "test.profile"
    f.write_text(MINI_PROFILE, encoding="utf-8")
    return profile_mm.model_from_file(str(f))


@pytest.fixture
def mini_req(requirements_mm: Any, tmp_path: Path) -> Any:
    f = tmp_path / "test.req"
    f.write_text(MINI_REQ, encoding="utf-8")
    return requirements_mm.model_from_file(str(f))
