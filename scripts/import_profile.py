"""CLI: Importiert bestehende CV-Dokumente (.docx) als .profile DSL via Claude API.

Aufruf:
    python scripts/import_profile.py <eingabe> [<eingabe2> ...] -o <ausgabe.profile>

Beispiele:
    python scripts/import_profile.py arbeitsdokumente/profil/ -o data/mein/mein.profile
    python scripts/import_profile.py cv_2024.docx cv_2025.docx -o draft.profile

Hinweis: benötigt ANTHROPIC_API_KEY in der Umgebung.
Eingaben können Einzeldateien oder Verzeichnisse (rekursiv .docx-Suche) sein.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.profile_importer import import_profile_documents


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Importiert CV-Dokumente als .profile-DSL via Claude API"
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="Eingabe-Datei(en) (.docx) oder Verzeichnis(se)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Pfad zur Ausgabe .profile-Datei",
    )
    args = parser.parse_args()

    try:
        result = import_profile_documents(args.inputs, args.output)
    except FileNotFoundError as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"Profil geschrieben: {result}")


if __name__ == "__main__":
    main()
