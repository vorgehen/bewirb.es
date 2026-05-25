"""
codegen.py -- Generiert aus grammar/profile.tx:
  src/models.py        -- Pydantic-Klassen fuer alle Grammatik-Entitaeten
  src/graph_schema.py  -- NetworkX-Knotendefinitionen
  web/schemas.py       -- FastAPI Response-Schemas

AUTO-GENERATED Zieldateien -- niemals manuell bearbeiten.
Aufruf: python codegen/codegen.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from textx import metamodel_from_file
from textx.const import RULE_COMMON

REPO_ROOT = Path(__file__).parent.parent
GRAMMAR_DIR = REPO_ROOT / "grammar"
SRC_DIR = REPO_ROOT / "src"
WEB_DIR = REPO_ROOT / "web"

_SKIP = frozenset(
    {
        # profile.tx
        "Profil",
        "ProfilElement",
        "Kategorie",
        "Proficiency",
        "SprachenLevel",
        "YearMonth",
        "YearMonthOrToday",
        # requirements.tx (Wurzel-/Choice-Regeln)
        "Anforderungen",
        "Angebotsstil",
        # knowledge.tx
        "Knowledge",
        "KnowledgeElement",
        "RelationType",
        "CompetencyAreaName",
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


def _py_annotation(
    attr: Any,
    response_suffix: bool = False,
    is_optional: bool = False,
) -> tuple[str, str]:
    """Gibt (Typ-Annotation, Standard-Wert) zurueck.

    Hinweis: TextX unterscheidet auf Attribut-Ebene nicht zwischen `x=Y` und
    `(x=Y)?`. Optionalität wird aus der Grammatik-Quelle gelesen
    (siehe _scan_optional_attrs).
    """
    base = _base_type(attr.cls) if attr.cls is not None else "str"
    if response_suffix and attr.ref and base not in ("str", "int", "float", "bool"):
        base = f"{base}Response"
    is_list = "*" in str(attr.mult)
    if is_list:
        return f"list[{base}]", " = []"
    if attr.ref:
        if is_optional:
            return f"{base} | None", " = None"
        return base, ""
    if base == "int":
        return "int", ""
    return "str", ' = ""'


# Pattern: (name=...)? in einem Klassen-Body. Greift Attribut-Name vor dem Gleichheitszeichen.
_OPTIONAL_ATTR_RE = re.compile(r"\(\s*'[^']*'?\s*(\w+)\s*=")


def _scan_optional_attrs(grammar_files: list[Path]) -> dict[str, set[str]]:
    """Scannt Grammatik-Quellen und erkennt optionale Attribute pro Klasse.

    Findet Patterns wie `('keyword:' name=Type)?` und sammelt den Attribut-Namen.
    Gibt {ClassName: {attr_name, ...}} zurück.
    """
    result: dict[str, set[str]] = {}
    class_def_re = re.compile(r"^(\w+):\s*$", re.MULTILINE)

    for gf in grammar_files:
        text = gf.read_text(encoding="utf-8")
        # Splitten an Class-Defs (Regelbeginn am Zeilenanfang mit `Name:`)
        positions = [(m.start(), m.group(1)) for m in class_def_re.finditer(text)]
        for i, (start, cls_name) in enumerate(positions):
            end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
            body = text[start:end]
            # `(... attr_name=Foo ...)?` finden
            optional_attrs = result.setdefault(cls_name, set())
            for m in re.finditer(r"\(([^()]*?)\)\s*\?", body):
                inner = m.group(1)
                # In dem optionalen Block Attribut-Zuweisungen suchen:
                #   name=Type oder name+=Type oder name=[Type] etc.
                for am in re.finditer(r"(\w+)\s*[+*]?=", inner):
                    optional_attrs.add(am.group(1))
    return result


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


def _collect_classes(metamodels: list[Any]) -> list[tuple[str, Any]]:
    """Sammelt Klassen aus mehreren Metamodellen, dedupliziert per Name."""
    seen: set[str] = set()
    result: list[tuple[str, Any]] = []
    for mm in metamodels:
        for name, cls in _common_classes(mm):
            if name in seen:
                continue
            seen.add(name)
            result.append((name, cls))
    return result


def _source_comment(grammar_files: list[Path]) -> str:
    names = ", ".join(f.name for f in grammar_files)
    return f"# Quelle: grammar/{{{names}}}  ->  codegen/codegen.py"


def generate_models(metamodels: list[Any], grammar_files: list[Path]) -> str:
    optional_map = _scan_optional_attrs(grammar_files)
    lines = [
        "# AUTO-GENERATED -- nicht manuell bearbeiten.",
        _source_comment(grammar_files),
        "from __future__ import annotations",
        "",
        "from pydantic import BaseModel",
    ]
    for name, cls in _collect_classes(metamodels):
        lines.append("")
        lines.append("")
        lines.append(f"class {name}(BaseModel):")
        for attr_name, attr in cls._tx_attrs.items():
            is_opt = attr_name in optional_map.get(name, set())
            ann, default = _py_annotation(attr, is_optional=is_opt)
            lines.append(f"    {attr_name}: {ann}{default}")
    lines.append("")
    return "\n".join(lines)


def generate_graph_schema(metamodels: list[Any], grammar_files: list[Path]) -> str:
    classes = _collect_classes(metamodels)
    lines = [
        "# AUTO-GENERATED -- nicht manuell bearbeiten.",
        _source_comment(grammar_files),
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


def generate_web_schemas(metamodels: list[Any], grammar_files: list[Path]) -> str:
    optional_map = _scan_optional_attrs(grammar_files)
    lines = [
        "# AUTO-GENERATED -- nicht manuell bearbeiten.",
        _source_comment(grammar_files),
        "from __future__ import annotations",
        "",
        "from pydantic import BaseModel",
    ]
    for name, cls in _collect_classes(metamodels):
        lines.append("")
        lines.append("")
        lines.append(f"class {name}Response(BaseModel):")
        for attr_name, attr in cls._tx_attrs.items():
            is_opt = attr_name in optional_map.get(name, set())
            ann, default = _py_annotation(attr, response_suffix=True, is_optional=is_opt)
            lines.append(f"    {attr_name}: {ann}{default}")
    lines.append("")
    return "\n".join(lines)


# Grammatiken die echte Entitäten beitragen (für Codegen).
# requirements.tx hat nur die Wurzel "Anforderungen" — wird von data_loader direkt
# via textx geladen, keine Pydantic-Modelle nötig.
_CODEGEN_GRAMMARS = ["profile.tx", "knowledge.tx"]


def main() -> None:
    grammar_files = [GRAMMAR_DIR / name for name in _CODEGEN_GRAMMARS]
    for f in grammar_files:
        if not f.exists():
            print(f"Grammatik nicht gefunden: {f}", file=sys.stderr)
            sys.exit(1)

    metamodels = [metamodel_from_file(str(f)) for f in grammar_files]
    print(f"Verarbeite {len(grammar_files)} Grammatik(en): {[f.name for f in grammar_files]}")

    targets = [
        (SRC_DIR / "models.py", generate_models(metamodels, grammar_files)),
        (SRC_DIR / "graph_schema.py", generate_graph_schema(metamodels, grammar_files)),
        (WEB_DIR / "schemas.py", generate_web_schemas(metamodels, grammar_files)),
    ]
    for path, code in targets:
        path.write_text(code, encoding="utf-8")
        print(f"OK  {path.relative_to(REPO_ROOT)}")

    print("Codegen abgeschlossen.")


if __name__ == "__main__":
    main()
