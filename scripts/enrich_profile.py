"""CLI: KI-gestützte Anreicherung von .profile-Daten.

Aktuell unterstützte Modi:

  kurzprofil — generiert ein neues Kurzprofil aus den Profil-Inhalten,
               zielgruppen-spezifisch.

Aufruf:
  python scripts/enrich_profile.py <profil.profile> --mode kurzprofil
  python scripts/enrich_profile.py <profil.profile> --mode kurzprofil --zielgruppe Consultant
  python scripts/enrich_profile.py <profil.profile> --mode kurzprofil --apply

Ohne --apply wird der neue Text nur angezeigt (Dry-Run).
Mit --apply wird die .profile-Datei in-place aktualisiert.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.data_loader import load_profile
from src.profile_enricher import generate_kurzprofil, update_kurzprofil_in_profile

# Ensure UTF-8 console output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]


def _run_kurzprofil(profile_path: Path, zielgruppe: str, apply: bool) -> None:
    profil = load_profile(profile_path)
    print(f"Profil:     {profile_path}")
    print(f"Zielgruppe: {zielgruppe}")
    print(f"Aktuell:    {profil.person.kurzprofil!r}")
    print()
    print("Rufe Claude API auf …")
    neu = generate_kurzprofil(profil, zielgruppe=zielgruppe)
    print()
    print("Neues Kurzprofil:")
    print("─" * 60)
    print(neu)
    print("─" * 60)
    print(f"({len(neu)} Zeichen)")
    print()

    if not apply:
        print("Dry-Run: --apply weglassen, um die Datei tatsächlich zu aktualisieren.")
        return

    updated = update_kurzprofil_in_profile(profile_path, neu)
    if updated:
        print(f"✓ kurzprofil-Feld in {profile_path} aktualisiert.")
    else:
        print(
            "✗ Konnte kein bestehendes kurzprofil-Feld in der Datei finden. "
            "Bitte manuell ergänzen.",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="KI-gestützte Anreicherung von .profile-Daten")
    parser.add_argument("profil", type=Path, help="Pfad zur .profile-Datei")
    parser.add_argument(
        "--mode",
        choices=["kurzprofil"],
        required=True,
        help="Welchen Aspekt anreichern",
    )
    parser.add_argument(
        "--zielgruppe",
        type=str,
        default="Standard",
        help="Zielgruppe für Tonalität "
        "(Behoerde / Consultant / StartUp / Wissenschaftlich / Standard / AIGovernance)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Ergebnis tatsächlich in die .profile-Datei schreiben (sonst Dry-Run)",
    )
    args = parser.parse_args()

    if not args.profil.exists():
        print(f"FEHLER: Profil-Datei nicht gefunden: {args.profil}", file=sys.stderr)
        sys.exit(1)

    if args.mode == "kurzprofil":
        _run_kurzprofil(args.profil, args.zielgruppe, args.apply)


if __name__ == "__main__":
    main()
