from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import anthropic
from anthropic.types import TextBlock

from src.data_loader import Anforderungen

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "extract_requirements.md"
MODEL = "claude-haiku-4-5-20251001"


def _load_prompt(ausschreibung: str) -> str:
    template = PROMPT_FILE.read_text(encoding="utf-8")
    return template.replace("{{ausschreibung}}", ausschreibung)


def _parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group()
    return dict(json.loads(text))


def extract_requirements(ausschreibung: str, name: str = "Extraktion") -> Anforderungen:
    """Extrahiert Anforderungen aus einem Ausschreibungstext via Claude API."""
    client = anthropic.Anthropic()
    prompt = _load_prompt(ausschreibung)

    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    block = message.content[0]
    if not isinstance(block, TextBlock):
        raise ValueError(f"Unerwarteter Block-Typ: {type(block)}")
    raw = block.text
    data = _parse_json(raw)

    return Anforderungen(
        name=name,
        rolle=str(data.get("rolle", "")),
        branchen=[str(b) for b in data.get("branchen") or []],
        must_have=[str(t) for t in data.get("must_have") or []],
        nice_to_have=[str(t) for t in data.get("nice_to_have") or []],
        keywords=[str(k) for k in data.get("keywords") or []],
        context=str(data.get("context", "")),
    )


def extract_and_write_req(
    ausschreibung: str, output: Path, name: str = "Extraktion"
) -> Anforderungen:
    """Extrahiert Anforderungen und schreibt eine .req-Datei."""
    anf = extract_requirements(ausschreibung, name=name)

    lines = [f"requirements {anf.name} {{", f'    rolle: "{anf.rolle}"']
    if anf.branchen:
        items = ", ".join(f'"{b}"' for b in anf.branchen)
        lines.append(f"    branchen: [{items}]")
    if anf.must_have:
        items = ", ".join(f'"{t}"' for t in anf.must_have)
        lines.append(f"    must_have: [{items}]")
    if anf.nice_to_have:
        items = ", ".join(f'"{t}"' for t in anf.nice_to_have)
        lines.append(f"    nice_to_have: [{items}]")
    if anf.keywords:
        items = ", ".join(f'"{k}"' for k in anf.keywords)
        lines.append(f"    keywords: [{items}]")
    if anf.context:
        lines.append(f'    context: "{anf.context}"')
    lines.append("}")

    output.write_text("\n".join(lines), encoding="utf-8")
    return anf
