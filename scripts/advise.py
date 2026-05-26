"""CLI: Bewertet Stellenangebote gegen das eigene Profil + Knowledge Layer.

Modi:
  Einzel:      python scripts/advise.py <profil.profile> <angebot.req>
  Portfolio:   python scripts/advise.py <profil.profile> --scan <angebote_dir>

Default-Ausgabe: textuell für Konsole. JSON via --json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.advisor import (
    GapType,
    evaluate_offer,
    scan_offers,
)
from src.data_loader import load_profile, load_requirements
from src.knowledge_loader import load_knowledge_base

# Ensure UTF-8 console output on Windows (PowerShell)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]


def print_single_offer(profil_path: Path, req_path: Path, as_json: bool) -> None:
    profil = load_profile(profil_path)
    anf = load_requirements(req_path)
    kb = load_knowledge_base()
    r = evaluate_offer(profil, anf, kb)

    if as_json:
        print(json.dumps(r.model_dump(), indent=2, ensure_ascii=False, default=str))
        return

    print(f"Angebot: {req_path.name}")
    print(f"Rolle:   {anf.rolle}")
    print(f"Empfehlung: {r.empfehlung}  (Match-Score: {r.score:.0%})")
    print()
    if r.matched_must_have:
        print(f"Treffer must_have:    {', '.join(r.matched_must_have)}")
    if r.matched_nice_to_have:
        print(f"Treffer nice_to_have: {', '.join(r.matched_nice_to_have)}")
    print()

    if r.strengths_underused:
        print("Stärken — aktuell unterkommuniziert:")
        for s in r.strengths_underused:
            print(f"  • {s}")
        print()

    if r.gaps:
        # Sortiert: artikulation < zertifizierung < erfahrung < strukturell
        order = {
            GapType.ARTIKULATION: 0,
            GapType.ZERTIFIZIERUNG: 1,
            GapType.ERFAHRUNG: 2,
            GapType.STRUKTURELL: 3,
        }
        print("Lücken nach Schließbarkeit:")
        for gap in sorted(r.gaps, key=lambda g: order[g.type]):
            marker = "✗" if gap.type == GapType.STRUKTURELL else "○"
            print(f"  {marker} [{gap.type.value}] {gap.term}")
            print(f"      → {gap.reason}")
        print()

    if r.boosts:
        print("Pluspunkte (aus opinions.knowledge):")
        for b in r.boosts:
            print(f"  + {b}")
        print()

    if r.warnings:
        print("Warnungen:")
        for w in r.warnings:
            print(f"  ! {w}")
        print()


def print_portfolio_scan(profil_path: Path, scan_dir: Path, as_json: bool) -> None:
    if not scan_dir.is_dir():
        print(f"FEHLER: {scan_dir} ist kein Verzeichnis", file=sys.stderr)
        sys.exit(1)

    result = scan_offers(profil_path, scan_dir)

    if as_json:
        print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
        return

    if not result.entries:
        print(f"Keine .req-Dateien in {scan_dir} gefunden.")
        return

    print(f"Portfolio-Scan: {len(result.entries)} Angebot(e)")
    print()
    print("Ranking:")
    for i, e in enumerate(result.entries, 1):
        print(f"  {i}. {e.file:40s} {e.score:5.0%}  {e.empfehlung}")
    print()

    if result.recurring_gaps:
        print("Wiederkehrende Lücken (in ≥2 Angeboten):")
        for term, count in result.recurring_gaps[:10]:
            print(f"  ! {term} ({count}x)")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bewertet Bewerbungs-Angebote gegen das eigene Profil"
    )
    parser.add_argument("profil", type=Path, help="Pfad zur .profile-Datei")
    parser.add_argument(
        "request",
        type=Path,
        nargs="?",
        default=None,
        help="Pfad zur einzelnen .req-Datei (für Einzel-Modus)",
    )
    parser.add_argument(
        "--scan",
        type=Path,
        default=None,
        help="Verzeichnis mit .req-Dateien (für Portfolio-Modus)",
    )
    parser.add_argument("--json", action="store_true", help="Ausgabe als JSON statt Text")
    args = parser.parse_args()

    if args.scan and args.request:
        print("FEHLER: --scan und einzelnes Angebot schließen sich aus", file=sys.stderr)
        sys.exit(2)
    if not args.scan and not args.request:
        print("FEHLER: entweder <angebot.req> oder --scan <dir> angeben", file=sys.stderr)
        sys.exit(2)

    if args.scan:
        print_portfolio_scan(args.profil, args.scan, args.json)
    else:
        print_single_offer(args.profil, args.request, args.json)


if __name__ == "__main__":
    main()
