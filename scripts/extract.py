"""CLI: Extrahiert Anforderungen aus einem Ausschreibungstext via Claude API.

Aufruf:
    python scripts/extract.py <ausschreibung.txt> [--output <name.req>] [--name JOB_ID]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.extractor import extract_and_write_req


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrahiert .req aus Ausschreibungstext")
    parser.add_argument("ausschreibung", type=Path, help="Textdatei mit der Ausschreibung")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Ausgabe .req Datei")
    parser.add_argument("--name", "-n", type=str, default=None, help="Name/ID der Anforderung")
    args = parser.parse_args()

    text = args.ausschreibung.read_text(encoding="utf-8")
    name = args.name or args.ausschreibung.stem.replace("-", "_").replace(" ", "_")
    out = args.output or args.ausschreibung.with_suffix(".req")

    anf = extract_and_write_req(text, out, name=name)

    print(f"Rolle:      {anf.rolle}")
    print(f"must_have:  {', '.join(anf.must_have)}")
    if anf.nice_to_have:
        print(f"nice_to_have: {', '.join(anf.nice_to_have)}")
    print(f"\nReq-Datei geschrieben: {out}")


if __name__ == "__main__":
    main()
