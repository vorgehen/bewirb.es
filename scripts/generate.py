"""CLI: Generiert ein maßgeschneidertes Profil aus .profile und .req Dateien.

Aufruf:
    python scripts/generate.py <profil.profile> [<anforderungen.req>] [--output <datei>]
    python scripts/generate.py <profil.profile> [<anforderungen.req>] --format word
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.data_loader import load_profile, load_requirements
from src.generators.markdown import generate_markdown
from src.graph_builder import build_graph
from src.matcher import match_profile_to_requirements
from src.pim_to_psm import transform


def main() -> None:
    parser = argparse.ArgumentParser(description="Generiert ein maßgeschneidertes Profil")
    parser.add_argument("profil", type=Path, help="Pfad zur .profile Datei")
    parser.add_argument(
        "anforderungen",
        type=Path,
        nargs="?",
        default=None,
        help="Pfad zur .req Datei (optional)",
    )
    parser.add_argument("--output", "-o", type=Path, default=None, help="Ausgabedatei")
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "word"],
        default="markdown",
        help="Ausgabeformat (Standard: markdown)",
    )
    parser.add_argument(
        "--template",
        "-t",
        type=Path,
        default=None,
        help="Pfad zur Word-Vorlage (nur mit --format word)",
    )
    args = parser.parse_args()

    profil = load_profile(args.profil)

    if args.anforderungen:
        anf = load_requirements(args.anforderungen)
        result = match_profile_to_requirements(profil, anf)
        print(f"Match-Score: {result.score:.0%}")
        print(f"Treffer must_have:  {', '.join(result.matched_must_have) or '—'}")
        if result.missing_must_have:
            print(f"Fehlend must_have:  {', '.join(result.missing_must_have)}")
        if result.matched_nice_to_have:
            print(f"Treffer nice_to_have: {', '.join(result.matched_nice_to_have)}")
        stem = args.anforderungen.stem
    else:
        from src.data_loader import Anforderungen

        anf = Anforderungen()
        stem = args.profil.stem

    g = build_graph(profil)
    psm = transform(g, anf)

    if args.format == "word":
        from src.generators.word import DEFAULT_TEMPLATE, generate_word_file

        template = args.template or DEFAULT_TEMPLATE
        if not template.exists():
            print(f"Vorlage nicht gefunden: {template}")
            print("Erstelle zuerst eine Vorlage mit: python scripts/create_template.py")
            sys.exit(1)
        out = args.output or Path(f"profil_{stem}.docx")
        generate_word_file(psm, profil, anf, out, template=template)
    else:
        out = args.output or Path(f"profil_{stem}.md")
        md = generate_markdown(psm, profil, anf)
        out.write_text(md, encoding="utf-8")

    print(f"\nProfil geschrieben: {out}")


if __name__ == "__main__":
    main()
