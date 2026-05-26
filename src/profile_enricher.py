"""KI-Anreicherung von .profile-Daten via Claude API.

Phase 11 (M2). Aktuell implementiert:

- Mode `kurzprofil`: generiert/aktualisiert das Kurzprofil-Feld aus
  Profilinhalten, zielgruppen-spezifisch in Tonalität.
- Mode `keywords`: schlägt marktrelevante zusätzliche Keywords pro
  Technologie vor (keine Web-Recherche, nur Claude-Trainingswissen).
- Mode `projekt`: verbessert description und achievements eines
  Projekt-Eintrags anhand eines anonymisierten Artefakt-Extrakts
  (NDA-sicher per AISE — Nutzer hat das Extrakt selbst bereinigt
  und freigegeben).

Nur das eigene Profil geht in die API — keine Kundendokumente.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import anthropic
from anthropic.types import TextBlock
from dotenv import load_dotenv

from src.data_loader import Profil

PROMPT_KURZPROFIL = Path(__file__).parent.parent / "prompts" / "generate_kurzprofil.md"
PROMPT_KEYWORDS = Path(__file__).parent.parent / "prompts" / "enrich_keywords.md"
PROMPT_PROJEKT = Path(__file__).parent.parent / "prompts" / "enrich_projekt.md"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4000  # Kurzprofil ~500 Zeichen, aber Reasoning-Modi brauchen Headroom
MAX_TOKENS_KEYWORDS = 8000  # Bei 30+ Technologien je 2-5 Vorschläge
MAX_TOKENS_PROJEKT = 4000  # Verbesserte description + achievements

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


# ─── Mode keywords ─────────────────────────────────────────────────────────


def _format_technologien_with_keywords(profil: Profil) -> str:
    """Tech-Liste mit existierenden Keywords im Format für den Prompt."""
    lines: list[str] = []
    for t in profil.technologien:
        kws = ", ".join(t.keywords) if t.keywords else "(keine)"
        lines.append(f"- {t.name} ({t.category}): bestehende Keywords: {kws}")
    return "\n".join(lines)


def suggest_keywords(profil: Profil) -> dict[str, list[str]]:
    """Ruft Claude API und gibt {tech_name: [vorschlaege]} zurück."""
    client = anthropic.Anthropic()
    template = PROMPT_KEYWORDS.read_text(encoding="utf-8")
    prompt = template.replace("{{technologien}}", _format_technologien_with_keywords(profil))
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS_KEYWORDS,
        messages=[{"role": "user", "content": prompt}],
    )
    block = message.content[0]
    if not isinstance(block, TextBlock):
        raise ValueError(f"Unerwarteter Block-Typ: {type(block)}")
    text = _strip_artifacts(block.text)

    result: dict[str, list[str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
            tech = str(obj.get("tech", ""))
            vorschlaege = [str(v) for v in obj.get("vorschlaege") or []]
            if tech and vorschlaege:
                result[tech] = vorschlaege
        except json.JSONDecodeError:
            continue
    return result


_TECHNOLOGY_BLOCK_RE = re.compile(
    r"(technology\s+(\w+)\s*\{[^}]*?keywords:\s*\[)([^\]]*?)(\])",
    re.DOTALL,
)


def update_keywords_in_profile(profile_path: Path, vorschlaege: dict[str, list[str]]) -> int:
    """Erweitert die keywords-Listen je technology-Block in-place.

    Nutzt vorschlaege als {tech_name: [neue_keywords]}-Mapping. Hängt
    neue Keywords ans Ende der bestehenden Liste an (keine Duplikate).
    Gibt die Anzahl tatsächlich aktualisierter technology-Blöcke zurück.
    """
    content = profile_path.read_text(encoding="utf-8")
    updates = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal updates
        prefix, tech_name, kws_inner, suffix = match.groups()
        if tech_name not in vorschlaege:
            return match.group(0)
        new_items = vorschlaege[tech_name]

        # Existierende Keywords parsen
        existing = []
        for s in re.findall(r'"((?:[^"\\]|\\.)*)"', kws_inner):
            existing.append(s)

        # Neue Items anhängen ohne Duplikate (case-insensitive)
        existing_lower = {e.lower() for e in existing}
        for item in new_items:
            if item.lower() not in existing_lower:
                existing.append(item)
                existing_lower.add(item.lower())

        formatted = ", ".join(f'"{_escape_dsl_string(e)}"' for e in existing)
        updates += 1
        return f"{prefix}{formatted}{suffix}"

    new_content = _TECHNOLOGY_BLOCK_RE.sub(_replace, content)
    if updates > 0:
        profile_path.write_text(new_content, encoding="utf-8")
    return updates


# ─── Mode projekt ──────────────────────────────────────────────────────────


class ProjektVorschlag:
    """Container für den von Claude gelieferten Verbesserungs-Vorschlag."""

    def __init__(self, description: str = "", achievements: list[str] | None = None) -> None:
        self.description = description
        self.achievements = achievements or []

    @property
    def hat_aenderung(self) -> bool:
        return bool(self.description) or bool(self.achievements)


def _find_projekt(profil: Profil, projekt_id: str) -> object:
    for p in profil.projekte:
        if p.name == projekt_id:
            return p
    raise KeyError(f"Projekt-ID {projekt_id!r} nicht im Profil gefunden.")


def _build_projekt_prompt(projekt: object, extrakt: str) -> str:
    template = PROMPT_PROJEKT.read_text(encoding="utf-8")
    tech_names = ", ".join(t.name for t in getattr(projekt, "uses", []) or []) or "(keine)"
    achievements = getattr(projekt, "achievements", []) or []
    ach_text = "\n".join(f"- {a}" for a in achievements) if achievements else "(keine)"
    substitutions = {
        "{{projekt_id}}": getattr(projekt, "name", ""),
        "{{projekt_title}}": getattr(projekt, "title", ""),
        "{{projekt_start}}": getattr(projekt, "start", ""),
        "{{projekt_end}}": getattr(projekt, "end", ""),
        "{{projekt_rolle}}": getattr(projekt, "rolle", ""),
        "{{projekt_tech}}": tech_names,
        "{{projekt_description}}": getattr(projekt, "description", "") or "(keine)",
        "{{projekt_achievements}}": ach_text,
        "{{extrakt}}": extrakt,
    }
    out = template
    for key, value in substitutions.items():
        out = out.replace(key, value)
    return out


def enrich_projekt(profil: Profil, projekt_id: str, extrakt: str) -> ProjektVorschlag:
    """Ruft Claude API mit Projekt-Eintrag + anonymisiertem Extrakt.

    Gibt ProjektVorschlag mit verbesserter description und achievements zurück.
    """
    projekt = _find_projekt(profil, projekt_id)
    client = anthropic.Anthropic()
    prompt = _build_projekt_prompt(projekt, extrakt)
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS_PROJEKT,
        messages=[{"role": "user", "content": prompt}],
    )
    block = message.content[0]
    if not isinstance(block, TextBlock):
        raise ValueError(f"Unerwarteter Block-Typ: {type(block)}")
    raw = _strip_artifacts(block.text).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        # Defensive: vielleicht ist nur das umschließende { ... } fehlerhaft
        # Versuche das erste JSON-Objekt im Text zu finden
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError(f"Claude-Antwort ist kein JSON: {raw[:200]}") from e
        data = json.loads(match.group(0))
    description = str(data.get("description", "") or "")
    achievements_raw = data.get("achievements") or []
    achievements = [str(a) for a in achievements_raw if str(a).strip()]
    return ProjektVorschlag(description=description, achievements=achievements)


# Findet einen projekt-Block mit gegebener ID. Greift weil DSL-Blöcke
# verschachtelte {} nicht enthalten (alle Felder sind flach).
def _projekt_block_re(projekt_id: str) -> re.Pattern[str]:
    escaped_id = re.escape(projekt_id)
    return re.compile(
        rf"(projekt\s+{escaped_id}\s*\{{)([^}}]*?)(\}})",
        re.DOTALL,
    )


_DESC_LINE_RE = re.compile(r'^(\s*description:\s*)"(?:[^"\\]|\\.)*"', re.MULTILINE)
_ACHIEVEMENTS_LINE_RE = re.compile(r"^(\s*achievements:\s*)\[[^\]]*\]", re.MULTILINE)


def update_projekt_in_profile(
    profile_path: Path, projekt_id: str, vorschlag: ProjektVorschlag
) -> bool:
    """Aktualisiert description und/oder achievements eines Projekt-Blocks
    in-place. Wenn ein Feld leer ist, wird es nicht überschrieben.

    Gibt True zurück, wenn mindestens ein Feld aktualisiert wurde.
    """
    content = profile_path.read_text(encoding="utf-8")
    block_re = _projekt_block_re(projekt_id)
    match = block_re.search(content)
    if match is None:
        return False
    prefix, body, suffix = match.groups()
    new_body = body
    changed = False

    if vorschlag.description:
        escaped = _escape_dsl_string(vorschlag.description)
        # Falls description-Zeile fehlt: einfügen vor dem schließenden }
        if _DESC_LINE_RE.search(new_body):
            new_body = _DESC_LINE_RE.sub(rf'\1"{escaped}"', new_body, count=1)
        else:
            new_body = new_body.rstrip("\n") + f'\n    description: "{escaped}"\n'
        changed = True

    if vorschlag.achievements:
        items = ", ".join(f'"{_escape_dsl_string(a)}"' for a in vorschlag.achievements)
        if _ACHIEVEMENTS_LINE_RE.search(new_body):
            new_body = _ACHIEVEMENTS_LINE_RE.sub(rf"\1[{items}]", new_body, count=1)
        else:
            new_body = new_body.rstrip("\n") + f"\n    achievements: [{items}]\n"
        changed = True

    if not changed:
        return False

    new_content = content[: match.start()] + prefix + new_body + suffix + content[match.end() :]
    profile_path.write_text(new_content, encoding="utf-8")
    return True
