"""CLI: Generiert ein maßgeschneidertes Markdown-Profil aus .profile und .req Dateien.

Aufruf:
    python scripts/generate.py <profil.profile> <anforderungen.req> [--output <datei.md>]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.data_loader import load_profile, load_requirements
from src.generators.markdown import generate_markdown
from src.graph_builder import build_graph
from src.matcher import match_profile_to_requirements
from src.pim_to_psm import transform


def main() -> None:
    parser = argparse.ArgumentParser(description="Generiert ein maßgeschneidertes Profil")
    parser.add_argument("profil", type=Path, help="Pfad zur .profile Datei")
    parser.add_argument("anforderungen", type=Path, help="Pfad zur .req Datei")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Ausgabedatei (.md)")
    args = parser.parse_args()

    profil = load_profile(args.profil)
    anf = load_requirements(args.anforderungen)

    result = match_profile_to_requirements(profil, anf)
    print(f"Match-Score: {result.score:.0%}")
    print(f"Treffer must_have:  {', '.join(result.matched_must_have) or '—'}")
    if result.missing_must_have:
        print(f"Fehlend must_have:  {', '.join(result.missing_must_have)}")
    if result.matched_nice_to_have:
        print(f"Treffer nice_to_have: {', '.join(result.matched_nice_to_have)}")

    g = build_graph(profil)
    psm = transform(g, anf)
    md = generate_markdown(psm, profil, anf)

    out = args.output or Path(f"profil_{args.anforderungen.stem}.md")
    out.write_text(md, encoding="utf-8")
    print(f"\nProfil geschrieben: {out}")


if __name__ == "__main__":
    main()
