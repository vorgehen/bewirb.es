"""KI-Anreicherung von .profile-Daten via Claude API.

Phase 11 (M2). Aktuell implementiert:

- Mode `kurzprofil`: generiert/aktualisiert das Kurzprofil-Feld aus
  Profilinhalten, zielgruppen-spezifisch in Tonalität.

Geplant:
- Mode `projekt`: Verbessert Projekt-Beschreibungen mit Artefakt-Input
  (Phase 11 + 11a NDA-Pipeline).
- Mode `keywords`: Web-Recherche für aktualisierte Technologie-Begriffe.

Nur das eigene Profil geht in die API — keine Kundendokumente.
"""

from __future__ import annotations

import re
from pathlib import Path

import anthropic
from anthropic.types import TextBlock
from dotenv import load_dotenv

from src.data_loader import Profil

PROMPT_KURZPROFIL = Path(__file__).parent.parent / "prompts" / "generate_kurzprofil.md"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1000

load_dotenv()


def _format_projekte(profil: Profil, n: int = 5) -> str:
    """Top-N Projekte (neueste zuerst) als kompakten Text."""
    sorted_projekte = sorted(profil.projekte, key=lambda p: p.start, reverse=True)
    lines: list[str] = []
    for p in sorted_projekte[:n]:
        auftraggeber = p.auftraggeber.label or p.auftraggeber.name if p.auftraggeber else ""
        techs = ", ".join(t.name for t in p.uses) if p.uses else ""
        line = f"- {p.start}–{p.end} {p.title} ({auftraggeber}, {p.rolle})"
        if techs:
            line += f" [{techs}]"
        lines.append(line)
    return "\n".join(lines)


def _format_top_technologien(profil: Profil, n: int = 10) -> str:
    """Top-N Technologien nach Jahren."""
    sorted_techs = sorted(profil.technologien, key=lambda t: t.years, reverse=True)
    return "\n".join(f"- {t.name} ({t.years}J, {t.proficiency})" for t in sorted_techs[:n])


def _format_werdegang(profil: Profil) -> str:
    """Werdegang-Stationen als kompakter Text."""
    sorted_wd = sorted(profil.werdegang, key=lambda w: w.start, reverse=True)
    return "\n".join(f"- {w.start}–{w.end} {w.titel} @ {w.arbeitgeber}" for w in sorted_wd)


def _format_schluesselkompetenz_kategorie(profil: Profil, kategorie: str) -> str:
    """Schluesselkompetenz-Kategorie als Komma-getrennt."""
    sk = profil.schluesselkompetenzen
    if sk is None:
        return ""
    items: list[str] = getattr(sk, kategorie, []) or []
    return ", ".join(items)


def _build_prompt(profil: Profil, zielgruppe: str) -> str:
    """Bereitet den Prompt mit Profil-Inhalten als Substitutionen vor."""
    template = PROMPT_KURZPROFIL.read_text(encoding="utf-8")
    substitutions = {
        "{{person_title}}": profil.person.title or "",
        "{{zielgruppe}}": zielgruppe or "Standard",
        "{{kurzprofil_alt}}": profil.person.kurzprofil or "(keines vorhanden)",
        "{{top_technologien}}": _format_top_technologien(profil),
        "{{projekte}}": _format_projekte(profil),
        "{{methoden}}": _format_schluesselkompetenz_kategorie(profil, "methodenkompetenz"),
        "{{fachgebiete}}": _format_schluesselkompetenz_kategorie(profil, "fachkompetenz"),
        "{{werdegang}}": _format_werdegang(profil),
    }
    out = template
    for key, value in substitutions.items():
        out = out.replace(key, value)
    return out


def _strip_artifacts(text: str) -> str:
    """Entfernt Code-Fences und führende/abschließende Anführungszeichen."""
    text = text.strip()
    fence_re = re.compile(r"^```(?:\w+)?\n(.*?)\n```$", re.DOTALL)
    m = fence_re.match(text)
    if m:
        text = m.group(1).strip()
    # Häufiger Fehler: Antwort in "..." gewrappt
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        text = text[1:-1].strip()
    return text


def generate_kurzprofil(profil: Profil, zielgruppe: str = "Standard") -> str:
    """Ruft Claude API und gibt einen neu generierten Kurzprofil-Text zurück."""
    client = anthropic.Anthropic()
    prompt = _build_prompt(profil, zielgruppe)
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    block = message.content[0]
    if not isinstance(block, TextBlock):
        raise ValueError(f"Unerwarteter Block-Typ: {type(block)}")
    return _strip_artifacts(block.text)


# ─── Profile-Datei-Manipulation ────────────────────────────────────────────


_KURZPROFIL_LINE_RE = re.compile(r'^(\s*kurzprofil:\s*)"(?:[^"\\]|\\.)*"', re.MULTILINE)


def _escape_dsl_string(s: str) -> str:
    """Escaped doppelte Anführungszeichen und Backslashes für TextX-Strings."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def update_kurzprofil_in_profile(profile_path: Path, neues_kurzprofil: str) -> bool:
    """Aktualisiert das kurzprofil-Feld im person-Block der .profile-Datei.

    Gibt True zurück, wenn ein Eintrag aktualisiert wurde, False sonst.
    Schreibt die Datei in-place.
    """
    content = profile_path.read_text(encoding="utf-8")
    escaped = _escape_dsl_string(neues_kurzprofil)
    new_line = rf'\1"{escaped}"'

    if _KURZPROFIL_LINE_RE.search(content):
        new_content = _KURZPROFIL_LINE_RE.sub(new_line, content, count=1)
        profile_path.write_text(new_content, encoding="utf-8")
        return True
    return False
