"""CLI: Erstellt eine Starter-Vorlage templates/profil.docx fuer den Word-Generator.

Aufruf:
    python scripts/create_template.py [--output templates/profil.docx]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.generators.word import create_default_template


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Erstellt eine Word-Vorlage fuer den Profil-Generator"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("templates/profil.docx"),
        help="Ausgabepfad fuer die Vorlage (Standard: templates/profil.docx)",
    )
    args = parser.parse_args()
    create_default_template(args.output)
    print(f"Vorlage erstellt: {args.output}")


if __name__ == "__main__":
    main()
