"""
codegen.py -- Generiert aus grammar/profile.tx:
  src/models.py        -- Pydantic-Klassen fuer alle Grammatik-Entitaeten
  src/graph_schema.py  -- NetworkX-Knotendefinitionen
  web/schemas.py       -- FastAPI Response-Schemas

AUTO-GENERATED Zieldateien -- niemals manuell bearbeiten.
Aufruf: python codegen/codegen.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from textx import metamodel_from_file
from textx.const import RULE_COMMON

REPO_ROOT = Path(__file__).parent.parent
GRAMMAR_FILE = REPO_ROOT / "grammar" / "profile.tx"
SRC_DIR = REPO_ROOT / "src"
WEB_DIR = REPO_ROOT / "web"

_SKIP = frozenset(
    {
        "Profil",
        "ProfilElement",
        "Kategorie",
        "Proficiency",
        "YearMonth",
        "YearMonthOrToday",
    }
)

_BUILTIN_CLS_NAMES = frozenset({"STRING", "INT", "FLOAT", "BOOL", "ID"})


def _base_type(attr_cls: Any) -> str:
    name = getattr(attr_cls, "__name__", "str")
    if name in ("STRING", "ID") or attr_cls is str:
        return "str"
    if name == "INT" or attr_cls is int:
        return "int"
    if name == "FLOAT" or attr_cls is float:
        return "float"
    if name == "BOOL" or attr_cls is bool:
        return "bool"
    if name in _BUILTIN_CLS_NAMES or hasattr(attr_cls, "_tx_type"):
        tx_type = getattr(attr_cls, "_tx_type", RULE_COMMON)
        if tx_type != RULE_COMMON:
            return "str"
    return name


def _py_annotation(attr: Any, response_suffix: bool = False) -> tuple[str, str]:
    """Gibt (Typ-Annotation, Standard-Wert) zurueck."""
    base = _base_type(attr.cls) if attr.cls is not None else "str"
    if response_suffix and attr.ref and base not in ("str", "int", "float", "bool"):
        base = f"{base}Response"
    is_list = "*" in str(attr.mult)
    if is_list:
        return f"list[{base}]", " = []"
    if attr.ref:
        return base, ""
    if base == "int":
        return "int", ""
    return "str", ' = ""'


def _common_classes(mm: Any) -> list[tuple[str, Any]]:
    return [
        (name, cls)
        for name, cls in mm._current_namespace.items()
        if (
            not name.startswith("_")
            and name not in _SKIP
            and hasattr(cls, "_tx_type")
            and cls._tx_type == RULE_COMMON
            and getattr(cls, "_tx_attrs", None)
        )
    ]


def generate_models(mm: Any) -> str:
    lines = [
        "# AUTO-GENERATED -- nicht manuell bearbeiten.",
        "# Quelle: grammar/profile.tx  ->  codegen/codegen.py",
        "from __future__ import annotations",
        "",
        "from pydantic import BaseModel",
    ]
    for name, cls in _common_classes(mm):
        lines.append("")
        lines.append("")
        lines.append(f"class {name}(BaseModel):")
        for attr_name, attr in cls._tx_attrs.items():
            ann, default = _py_annotation(attr)
            lines.append(f"    {attr_name}: {ann}{default}")
    lines.append("")
    return "\n".join(lines)


def generate_graph_schema(mm: Any) -> str:
    classes = _common_classes(mm)
    lines = [
        "# AUTO-GENERATED -- nicht manuell bearbeiten.",
        "# Quelle: grammar/profile.tx  ->  codegen/codegen.py",
        "",
        "NODE_TYPES: list[str] = [",
    ]
    for name, _ in classes:
        lines.append(f'    "{name}",')
    lines += ["]", ""]
    for name, cls in classes:
        attr_lines = [f'    "{a}",' for a in cls._tx_attrs]
        lines.append(f"{name.upper()}_ATTRS: list[str] = [")
        lines.extend(attr_lines)
        lines.append("]")
    lines.append("")
    return "\n".join(lines)


def generate_web_schemas(mm: Any) -> str:
    lines = [
        "# AUTO-GENERATED -- nicht manuell bearbeiten.",
        "# Quelle: grammar/profile.tx  ->  codegen/codegen.py",
        "from __future__ import annotations",
        "",
        "from pydantic import BaseModel",
    ]
    for name, cls in _common_classes(mm):
        lines.append("")
        lines.append("")
        lines.append(f"class {name}Response(BaseModel):")
        for attr_name, attr in cls._tx_attrs.items():
            ann, default = _py_annotation(attr, response_suffix=True)
            lines.append(f"    {attr_name}: {ann}{default}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    if not GRAMMAR_FILE.exists():
        print(f"Grammatik nicht gefunden: {GRAMMAR_FILE}", file=sys.stderr)
        sys.exit(1)

    mm = metamodel_from_file(str(GRAMMAR_FILE))

    targets = [
        (SRC_DIR / "models.py", generate_models(mm)),
        (SRC_DIR / "graph_schema.py", generate_graph_schema(mm)),
        (WEB_DIR / "schemas.py", generate_web_schemas(mm)),
    ]
    for path, code in targets:
        path.write_text(code, encoding="utf-8")
        print(f"OK  {path.relative_to(REPO_ROOT)}")

    print("Codegen abgeschlossen.")


if __name__ == "__main__":
    main()
