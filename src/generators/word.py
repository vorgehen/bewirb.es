from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx
from docx import Document
from docxtpl import DocxTemplate, Listing

from src.data_loader import Anforderungen, Profil

DEFAULT_TEMPLATE = Path(__file__).parent.parent.parent / "templates" / "profil.docx"


def _clear_and_set(cell: Any, text: str) -> None:
    para = cell.paragraphs[0]
    para.clear()
    para.add_run(text)


def create_default_template(output: Path) -> None:
    """Creates a starter Word template with Jinja2 placeholders for docxtpl."""
    doc = Document()

    doc.add_heading("{{ person_title }}", level=1)
    doc.add_paragraph("{{ contact_email }}  |  {{ contact_location }}")

    doc.add_paragraph("{%p if contact_phone %}")
    doc.add_paragraph("Tel.: {{ contact_phone }}")
    doc.add_paragraph("{%p endif %}")

    doc.add_paragraph("{%p if zielrolle %}")
    doc.add_paragraph("Zielrolle: {{ zielrolle }}")
    doc.add_paragraph("{%p endif %}")

    # Schlüssel-Kompetenzen: loop-start row / data row / loop-end row
    doc.add_heading("Schlüssel-Kompetenzen", level=2)
    sk_table = doc.add_table(rows=3, cols=1)
    sk_table.style = "Table Grid"
    _clear_and_set(sk_table.rows[0].cells[0], "{%tr for sk in schluessel_kompetenzen %}")
    _clear_and_set(sk_table.rows[1].cells[0], "{{ sk }}")
    _clear_and_set(sk_table.rows[2].cells[0], "{%tr endfor %}")

    # Technologiekompetenz: header / loop-start / data / loop-end
    doc.add_heading("Technologiekompetenz", level=2)
    tech_table = doc.add_table(rows=4, cols=4)
    tech_table.style = "Table Grid"
    for i, label in enumerate(["Technologie", "Kategorie", "Level", "Jahre"]):
        cell = tech_table.rows[0].cells[i]
        _clear_and_set(cell, label)
        cell.paragraphs[0].runs[0].bold = True
    _clear_and_set(tech_table.rows[1].cells[0], "{%tr for tech in technologien %}")
    dr = tech_table.rows[2]
    _clear_and_set(dr.cells[0], "{{ tech.name }}")
    _clear_and_set(dr.cells[1], "{{ tech.category }}")
    _clear_and_set(dr.cells[2], "{{ tech.proficiency }}")
    _clear_and_set(dr.cells[3], "{{ tech.years }} J.")
    _clear_and_set(tech_table.rows[3].cells[0], "{%tr endfor %}")

    # Projekterfahrung: header / loop-start / data / loop-end
    doc.add_heading("Projekterfahrung", level=2)
    proj_table = doc.add_table(rows=4, cols=4)
    proj_table.style = "Table Grid"
    for i, label in enumerate(["Zeitraum / Rolle", "Projekt", "Auftraggeber", "Technologien"]):
        cell = proj_table.rows[0].cells[i]
        _clear_and_set(cell, label)
        cell.paragraphs[0].runs[0].bold = True
    _clear_and_set(proj_table.rows[1].cells[0], "{%tr for p in projekte %}")
    pr = proj_table.rows[2]
    _clear_and_set(pr.cells[0], "{{ p.start }}–{{ p.end }}")
    pr.cells[0].add_paragraph("{{ p.rolle }}")
    _clear_and_set(pr.cells[1], "{{ p.title }}")
    pr.cells[1].add_paragraph("{{ p.description }}")
    pr.cells[1].add_paragraph("{{ p.achievements_str }}")
    _clear_and_set(pr.cells[2], "{{ p.auftraggeber_label }}")
    _clear_and_set(pr.cells[3], "{{ p.tech_str }}")
    _clear_and_set(proj_table.rows[3].cells[0], "{%tr endfor %}")

    # Ausbildung: header / loop-start / data / loop-end
    doc.add_heading("Ausbildung", level=2)
    aus_table = doc.add_table(rows=4, cols=3)
    aus_table.style = "Table Grid"
    for i, label in enumerate(["Zeitraum", "Abschluss", "Institution"]):
        cell = aus_table.rows[0].cells[i]
        _clear_and_set(cell, label)
        cell.paragraphs[0].runs[0].bold = True
    _clear_and_set(aus_table.rows[1].cells[0], "{%tr for a in ausbildungen %}")
    ar = aus_table.rows[2]
    _clear_and_set(ar.cells[0], "{{ a.start }}–{{ a.end }}")
    _clear_and_set(ar.cells[1], "{{ a.title }}")
    ar.cells[1].add_paragraph("{{ a.abschluss }}")
    _clear_and_set(ar.cells[2], "{{ a.institution }}")
    _clear_and_set(aus_table.rows[3].cells[0], "{%tr endfor %}")

    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output))


def _build_context(psm: nx.DiGraph[str], profil: Profil, anf: Anforderungen) -> dict[str, Any]:
    matched_techs = [
        d["name"]
        for _, d in psm.nodes(data=True)
        if d.get("type") == "Technologiekompetenz" and d.get("matched")
    ]

    technologien: list[dict[str, Any]] = []
    for tech in sorted(profil.technologien, key=lambda t: t.years, reverse=True):
        technologien.append(
            {
                "name": tech.name,
                "category": tech.category,
                "proficiency": tech.proficiency,
                "years": str(tech.years),
            }
        )

    projekte: list[dict[str, Any]] = []
    for p in profil.projekte:
        tech_str = ", ".join(t.name for t in p.uses)
        achievements = "\n".join(f"• {a}" for a in p.achievements)
        projekte.append(
            {
                "title": p.title,
                "start": p.start,
                "end": p.end,
                "auftraggeber_label": p.auftraggeber.label or p.auftraggeber.name,
                "rolle": p.rolle,
                "tech_str": tech_str,
                "description": p.description,
                "achievements_str": Listing(achievements) if achievements else "",
            }
        )

    ausbildungen: list[dict[str, Any]] = [
        {
            "title": a.title,
            "institution": a.institution,
            "start": a.start,
            "end": a.end,
            "abschluss": a.abschluss,
        }
        for a in profil.ausbildungen
    ]

    c = profil.person.contact
    return {
        "person_title": profil.person.title,
        "contact_email": c.email,
        "contact_phone": c.phone,
        "contact_location": c.location,
        "zielrolle": anf.rolle,
        "schluessel_kompetenzen": matched_techs,
        "technologien": technologien,
        "projekte": projekte,
        "ausbildungen": ausbildungen,
    }


def generate_word_file(
    psm: nx.DiGraph[str],
    profil: Profil,
    anf: Anforderungen,
    output: Path,
    template: Path = DEFAULT_TEMPLATE,
) -> None:
    doc = DocxTemplate(str(template))
    context = _build_context(psm, profil, anf)
    doc.render(context)
    doc.save(str(output))
