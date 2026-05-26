"""CLI: Anonymisiert Dokumente lokal (Level 1, regelbasiert).

Aufruf:
  python scripts/anonymize_doc.py <input.docx>
  python scripts/anonymize_doc.py <verzeichnis/> -o extrakt.txt
  python scripts/anonymize_doc.py <verzeichnis/> -o extrakt.txt --config my_config.yaml
  python scripts/anonymize_doc.py <input.docx> --audit-only

Ohne Output-Pfad wird der anonymisierte Text auf stdout geschrieben.
--audit-only zeigt nur das Audit-Log, kein Text-Output.

Standard-Konfig: anonymize_config.yaml im Projekt-Root (falls vorhanden).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.anonymizer import anonymize_documents

# UTF-8 stdout auf Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

DEFAULT_CONFIG = Path(__file__).parent.parent / "anonymize_config.yaml"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Anonymisiert Dokumente lokal (Level 1, regelbasiert)"
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="Eingabe-Datei(en) oder Verzeichnis(se) — .docx, .txt, .md",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Ausgabe-Pfad für anonymisierten Text (Default: stdout)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help=f"Pfad zur Konfig (Default: {DEFAULT_CONFIG.name} im Projekt-Root)",
    )
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="Nur das Audit-Log auf stderr ausgeben, kein anonymisierter Text",
    )
    args = parser.parse_args()

    config_path = args.config or (DEFAULT_CONFIG if DEFAULT_CONFIG.exists() else None)

    try:
        text, audit = anonymize_documents(args.inputs, config_path)
    except FileNotFoundError as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)

    if args.audit_only:
        print(audit.format(), file=sys.stderr)
        return

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Anonymisierter Text geschrieben: {args.output}", file=sys.stderr)
    else:
        print(text)

    # Audit immer auf stderr (auch ohne --audit-only) damit es sichtbar bleibt
    print(file=sys.stderr)
    print(audit.format(), file=sys.stderr)


if __name__ == "__main__":
    main()
