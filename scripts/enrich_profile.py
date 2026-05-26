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
from src.profile_enricher import (
    enrich_projekt,
    generate_kurzprofil,
    suggest_keywords,
    update_keywords_in_profile,
    update_kurzprofil_in_profile,
    update_projekt_in_profile,
)

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


def _run_keywords(profile_path: Path, apply: bool) -> None:
    profil = load_profile(profile_path)
    print(f"Profil:     {profile_path}")
    print(f"{len(profil.technologien)} Technologien zur Analyse")
    print()
    print("Rufe Claude API auf …")
    vorschlaege = suggest_keywords(profil)
    print()

    if not vorschlaege:
        print("Keine Vorschläge zurückgegeben.")
        return

    print(f"Vorschläge für {len(vorschlaege)} Technologien:")
    print("─" * 60)
    for tech, items in vorschlaege.items():
        print(f"  {tech}")
        print(f"    + {', '.join(items)}")
    print("─" * 60)
    print()

    if not apply:
        print("Dry-Run: --apply weglassen, um die Vorschläge tatsächlich anzuwenden.")
        return

    count = update_keywords_in_profile(profile_path, vorschlaege)
    print(f"✓ {count} technology-Blöcke in {profile_path} aktualisiert.")


def _run_projekt(
    profile_path: Path, projekt_id: str | None, preprocess: Path | None, apply: bool
) -> None:
    if not projekt_id:
        print("FEHLER: --projekt-id ist Pflicht bei --mode projekt", file=sys.stderr)
        sys.exit(2)
    if not preprocess:
        print(
            "FEHLER: --preprocess ist Pflicht bei --mode projekt (NDA-Schutz).\n"
            "        Bitte ein anonymisiertes Extrakt übergeben (siehe scripts/anonymize_doc.py).",
            file=sys.stderr,
        )
        sys.exit(2)
    if not preprocess.exists():
        print(f"FEHLER: Extrakt nicht gefunden: {preprocess}", file=sys.stderr)
        sys.exit(1)

    profil = load_profile(profile_path)
    try:
        projekt = next(p for p in profil.projekte if p.name == projekt_id)
    except StopIteration:
        print(
            f"FEHLER: Projekt-ID {projekt_id!r} nicht im Profil. "
            f"Verfügbar: {', '.join(p.name for p in profil.projekte)}",
            file=sys.stderr,
        )
        sys.exit(1)

    extrakt = preprocess.read_text(encoding="utf-8")
    print(f"Profil:     {profile_path}")
    print(f"Projekt:    {projekt_id} — {projekt.title}")
    print(f"Extrakt:    {preprocess} ({len(extrakt):,} Zeichen)")
    print()
    print("Aktuelle description:")
    print(f"  {projekt.description or '(leer)'}")
    print()
    print("Aktuelle achievements:")
    if projekt.achievements:
        for a in projekt.achievements:
            print(f"  • {a}")
    else:
        print("  (keine)")
    print()
    print("Rufe Claude API auf …")
    vorschlag = enrich_projekt(profil, projekt_id, extrakt)
    print()
    print("Neue description:")
    print("─" * 60)
    print(vorschlag.description or "(keine Änderung vorgeschlagen)")
    print("─" * 60)
    print()
    print("Neue achievements:")
    print("─" * 60)
    if vorschlag.achievements:
        for a in vorschlag.achievements:
            print(f"  • {a}")
    else:
        print("(keine Änderung vorgeschlagen)")
    print("─" * 60)
    print()

    if not apply:
        print("Dry-Run: --apply weglassen, um die Änderungen tatsächlich zu schreiben.")
        return

    updated = update_projekt_in_profile(profile_path, projekt_id, vorschlag)
    if updated:
        print(f"✓ Projekt {projekt_id} in {profile_path} aktualisiert.")
    else:
        print(
            f"✗ Konnte Projekt-Block {projekt_id!r} nicht aktualisieren.",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="KI-gestützte Anreicherung von .profile-Daten")
    parser.add_argument("profil", type=Path, help="Pfad zur .profile-Datei")
    parser.add_argument(
        "--mode",
        choices=["kurzprofil", "keywords", "projekt"],
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
        "--projekt-id",
        type=str,
        default=None,
        help="Projekt-ID im Profil (nur für --mode projekt)",
    )
    parser.add_argument(
        "--preprocess",
        type=Path,
        default=None,
        help="Pfad zu anonymisiertem Artefakt-Extrakt (nur für --mode projekt)",
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
    elif args.mode == "keywords":
        _run_keywords(args.profil, args.apply)
    elif args.mode == "projekt":
        _run_projekt(args.profil, args.projekt_id, args.preprocess, args.apply)


if __name__ == "__main__":
    main()
