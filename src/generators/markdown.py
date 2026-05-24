from __future__ import annotations

import networkx as nx

from src.data_loader import Anforderungen, Profil


def generate_markdown(psm: nx.DiGraph[str], profil: Profil, anf: Anforderungen) -> str:
    lines: list[str] = []

    lines.append(f"# Profil: {profil.person.title}")
    if anf.rolle:
        lines.append(f"\n**Zielrolle:** {anf.rolle}\n")

    c = profil.person.contact
    if c.email:
        lines.append(f"**Kontakt:** {c.email}")
    if c.location:
        lines.append(f"**Standort:** {c.location}")
    if c.linkedin:
        lines.append(f"**LinkedIn:** {c.linkedin}")
    lines.append("")

    matched_techs = [
        d["name"]
        for _, d in psm.nodes(data=True)
        if d.get("type") == "Technologiekompetenz" and d.get("matched")
    ]
    if matched_techs:
        lines.append("## Schluessel-Kompetenzen (Treffer)")
        for t in matched_techs:
            lines.append(f"- {t}")
        lines.append("")

    lines.append("## Technologiekompetenz")
    for tech in sorted(profil.technologien, key=lambda t: t.years, reverse=True):
        node_id = f"Technologiekompetenz:{tech.name}"
        node_data = psm.nodes.get(node_id, {})
        marker = " ✓" if node_data.get("matched") else ""
        lines.append(
            f"- **{tech.name}**{marker} — {tech.proficiency}, {tech.years} Jahre ({tech.category})"
        )
    lines.append("")

    lines.append("## Projekterfahrung")
    for projekt in profil.projekte:
        lines.append(f"\n### {projekt.title}")
        lines.append(f"**Zeitraum:** {projekt.start} – {projekt.end}")
        lines.append(f"**Auftraggeber:** {projekt.auftraggeber.label or projekt.auftraggeber.name}")
        lines.append(f"**Rolle:** {projekt.rolle}")
        if projekt.uses:
            tech_str = ", ".join(t.name for t in projekt.uses)
            lines.append(f"**Technologien:** {tech_str}")
        if projekt.description:
            lines.append(f"\n{projekt.description}")
        if projekt.achievements:
            lines.append("\n**Ergebnisse:**")
            for a in projekt.achievements:
                lines.append(f"- {a}")
    lines.append("")

    if profil.ausbildungen:
        lines.append("## Ausbildung")
        for ausb in profil.ausbildungen:
            lines.append(f"\n### {ausb.title}")
            lines.append(f"**Institution:** {ausb.institution}")
            lines.append(f"**Zeitraum:** {ausb.start} – {ausb.end}")
            if ausb.abschluss:
                lines.append(f"**Abschluss:** {ausb.abschluss}")
        lines.append("")

    return "\n".join(lines)
