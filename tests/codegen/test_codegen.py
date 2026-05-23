from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.snapshot]

REPO_ROOT = Path(__file__).parent.parent.parent
CODEGEN_SCRIPT = REPO_ROOT / "codegen" / "codegen.py"
MODELS_PY = REPO_ROOT / "src" / "models.py"
GRAPH_SCHEMA_PY = REPO_ROOT / "src" / "graph_schema.py"
WEB_SCHEMAS_PY = REPO_ROOT / "web" / "schemas.py"


@pytest.fixture(scope="module")
def generated(tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    result = subprocess.run(
        [sys.executable, str(CODEGEN_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"Codegen fehlgeschlagen:\n{result.stderr}"
    return {
        "models": MODELS_PY.read_text(encoding="utf-8"),
        "graph_schema": GRAPH_SCHEMA_PY.read_text(encoding="utf-8"),
        "web_schemas": WEB_SCHEMAS_PY.read_text(encoding="utf-8"),
    }


def test_codegen_exits_zero(generated: dict[str, str]) -> None:
    assert MODELS_PY.exists()


def test_models_py_header(generated: dict[str, str]) -> None:
    assert "AUTO-GENERATED" in generated["models"]
    assert "grammar/profile.tx" in generated["models"]
    assert "BaseModel" in generated["models"]


def test_models_py_contains_domain_classes(generated: dict[str, str]) -> None:
    for cls in (
        "Projekterfahrung",
        "Technologiekompetenz",
        "Person",
        "Auftraggeber",
        "Branche",
        "Ausbildung",
    ):
        assert cls in generated["models"], f"{cls} fehlt in models.py"


def test_models_py_is_valid_python(generated: dict[str, str]) -> None:
    compile(generated["models"], "models.py", "exec")


def test_graph_schema_node_types(generated: dict[str, str]) -> None:
    assert "NODE_TYPES" in generated["graph_schema"]
    assert "Projekterfahrung" in generated["graph_schema"]
    assert "Technologiekompetenz" in generated["graph_schema"]


def test_graph_schema_is_valid_python(generated: dict[str, str]) -> None:
    compile(generated["graph_schema"], "graph_schema.py", "exec")


def test_web_schemas_response_classes(generated: dict[str, str]) -> None:
    assert (
        "ProjekerfahrungResponse" in generated["web_schemas"]
        or "ProjekterfahrungResponse" in generated["web_schemas"]
    )
    assert "TechnologiekompetenzResponse" in generated["web_schemas"]


def test_web_schemas_is_valid_python(generated: dict[str, str]) -> None:
    compile(generated["web_schemas"], "schemas.py", "exec")
