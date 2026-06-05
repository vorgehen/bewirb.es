from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docxtpl import DocxTemplate, Listing

from src.data_loader import Anforderungen, Profil

DEFAULT_TEMPLATE = Path(__file__).parent.parent.parent / "templates" / "profil.docx"


def _fmt_geburtstag(d: str | None) -> str:
    if not d:
        return ""
    year, month, day = d.split("-")
    return f"{day}.{month}.{year}"


def _fmt_date(d: str) -> str:
    if d == "today":
        return "heute"
    year, month = d.split("-")
    return f"{month}.{year}"


def _append_field(para: Any, field_code: str) -> None:
    r1 = OxmlElement("w:r")
    fc1 = OxmlElement("w:fldChar")
    fc1.set(qn("w:fldCharType"), "begin")
    r1.append(fc1)
    r2 = OxmlElement("w:r")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {field_code} "
    r2.append(instr)
    r3 = OxmlElement("w:r")
    fc3 = OxmlElement("w:fldChar")
    fc3.set(qn("w:fldCharType"), "end")
    r3.append(fc3)
    para._p.append(r1)
    para._p.append(r2)
    para._p.append(r3)


def _remove_borders(table: Any) -> None:
    tbl = table._tbl
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)
    tblBorders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:val"), "none")
        node.set(qn("w:sz"), "0")
        node.set(qn("w:space"), "0")
        node.set(qn("w:color"), "auto")
        tblBorders.append(node)
    tblPr.append(tblBorders)


def _set_cell_padding(table: Any, dxa: int = 40) -> None:
    tbl = table._tbl
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)
    tblCellMar = OxmlElement("w:tblCellMar")
    for side in ("top", "left", "bottom", "right"):
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), str(dxa))
        node.set(qn("w:type"), "dxa")
        tblCellMar.append(node)
    tblPr.append(tblCellMar)


def _no_row_split(table: Any) -> None:
    for row in table.rows:
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        cantSplit = OxmlElement("w:cantSplit")
        cantSplit.set(qn("w:val"), "1")
        trPr.append(cantSplit)


def _clear_and_set(cell: Any, text: str) -> None:
    para = cell.paragraphs[0]
    para.clear()
    para.add_run(text)


def _add_table_loop(
    doc: Document,
    headers: list[str],
    cell_templates: list[str],
) -> None:
    """Fügt eine Tabelle mit Header / Loop-Start / Data / Loop-End hinzu.

    headers gibt die Spalten-Titel. cell_templates muss exakt so viele
    Einträge haben wie headers — jeweils der Jinja-Ausdruck für die Datenzeile.
    Loop-Variable: 'item'.
    """
    cols = len(headers)
    table = doc.add_table(rows=4, cols=cols)
    table.style = "Table Grid"
    for i, label in enumerate(headers):
        cell = table.rows[0].cells[i]
        _clear_and_set(cell, label)
        cell.paragraphs[0].runs[0].bold = True
    _clear_and_set(table.rows[1].cells[0], "{%tr for item in items %}")
    for i, expr in enumerate(cell_templates):
        _clear_and_set(table.rows[2].cells[i], expr)
    _clear_and_set(table.rows[3].cells[0], "{%tr endfor %}")


def _add_spiegelstrich_numbering(doc: Document) -> int:
    """Fügt eine Numbering-Definition mit – als Bullet hinzu. Gibt numId zurück."""
    try:
        numbering_part = doc.part.numbering_part
    except (KeyError, AttributeError):
        tmp = doc.add_paragraph("x")
        tmp.style = doc.styles["List Bullet"]
        numbering_part = doc.part.numbering_part
        tmp._element.getparent().remove(tmp._element)

    numbering_el = numbering_part._element

    abstracts = numbering_el.findall(qn("w:abstractNum"))
    next_abstract_id = (
        max((int(a.get(qn("w:abstractNumId"), -1)) for a in abstracts), default=-1) + 1
    )
    nums = numbering_el.findall(qn("w:num"))
    next_num_id = max((int(n.get(qn("w:numId"), 0)) for n in nums), default=0) + 1

    abstract_num = OxmlElement("w:abstractNum")
    abstract_num.set(qn("w:abstractNumId"), str(next_abstract_id))

    lvl = OxmlElement("w:lvl")
    lvl.set(qn("w:ilvl"), "0")
    for tag, val in [("w:start", "1"), ("w:numFmt", "bullet")]:
        e = OxmlElement(tag)
        e.set(qn("w:val"), val)
        lvl.append(e)
    lvl_text = OxmlElement("w:lvlText")
    lvl_text.set(qn("w:val"), "–")
    lvl.append(lvl_text)
    lvl_jc = OxmlElement("w:lvlJc")
    lvl_jc.set(qn("w:val"), "left")
    lvl.append(lvl_jc)
    ppr = OxmlElement("w:pPr")
    ind = OxmlElement("w:ind")
    ind.set(qn("w:left"), "360")
    ind.set(qn("w:hanging"), "180")
    ppr.append(ind)
    lvl.append(ppr)
    abstract_num.append(lvl)

    first_num = numbering_el.find(qn("w:num"))
    if first_num is not None:
        first_num.addprevious(abstract_num)
    else:
        numbering_el.append(abstract_num)

    num = OxmlElement("w:num")
    num.set(qn("w:numId"), str(next_num_id))
    abs_id = OxmlElement("w:abstractNumId")
    abs_id.set(qn("w:val"), str(next_abstract_id))
    num.append(abs_id)
    numbering_el.append(num)
    return next_num_id


def _apply_list_numbering(paragraph: Any, num_id: int) -> None:
    """Wendet eine Numbering-Definition auf einen Absatz an."""
    ppr = paragraph._p.get_or_add_pPr()
    num_pr = OxmlElement("w:numPr")
    ilvl = OxmlElement("w:ilvl")
    ilvl.set(qn("w:val"), "0")
    num_id_el = OxmlElement("w:numId")
    num_id_el.set(qn("w:val"), str(num_id))
    num_pr.extend([ilvl, num_id_el])
    ppr.append(num_pr)


def create_default_template(output: Path) -> None:
    """Creates a starter Word template with Jinja2 placeholders for docxtpl.

    Aufbau:
      1. Kopf: Person + Kontakt
      2. Kurzprofil (optional)
      3. Zielrolle (optional)
      4. Schlüsselkompetenzen (zielgruppen-spezifisch geordnet und benannt)
      5. IT-Know-How (Wissensgebiete in Aneignungs-Reihenfolge)
      6. Projekterfahrung
      7. Werdegang (Festanstellungen)
      8. Ausbildung
      9. Zertifikate
     10. Sprachen
     11. Persönliche Daten (optional)
    """
    doc = Document()

    for level in range(1, 4):
        style = doc.styles[f"Heading {level}"]
        style.font.color.rgb = RGBColor(0, 0, 0)

    # ─── 1. Kopf (2 Spalten ohne Rahmen) ───────────────────────────────────
    header_table = doc.add_table(rows=1, cols=2)
    lc = header_table.rows[0].cells[0]
    rc = header_table.rows[0].cells[1]

    # Linke Spalte: Überschrift + Name + Qualifikation
    p_title = lc.paragraphs[0]
    p_title.style = doc.styles["Heading 1"]
    p_title.clear()
    p_title.add_run("Lebenslauf / Profil")

    p_name = lc.add_paragraph()
    run_name = p_name.add_run("{{ person_name }}")
    run_name.bold = True
    run_name.font.size = Pt(13)
    p_name.paragraph_format.space_before = Pt(6)
    p_name.paragraph_format.space_after = Pt(0)

    p_qual = lc.add_paragraph("{{ person_qualifikation }}")
    p_qual.paragraph_format.space_before = Pt(0)
    p_qual.paragraph_format.space_after = Pt(0)

    # Rechte Spalte: Adresse + Kontakt, rechtsbündig, kein Abstand
    def _rc(text: str, gap_after: bool = False) -> None:
        p = rc.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6) if gap_after else Pt(0)

    p0 = rc.paragraphs[0]
    p0.clear()
    p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(0)
    p0.add_run("{{ contact_strasse }}")
    _rc("{{ contact_plz_ort }}", gap_after=True)
    _rc("{%p if contact_phone %}")
    _rc("Mobil: {{ contact_phone }}")
    _rc("{%p endif %}")
    _rc("{%p if contact_festnetz %}")
    _rc("Festnetz: {{ contact_festnetz }}")
    _rc("{%p endif %}")
    _rc("E-Mail: {{ contact_email }}")
    _rc("{%p if contact_linkedin %}")
    _rc("LinkedIn: {{ contact_linkedin }}")
    _rc("{%p endif %}")
    _rc("{%p if contact_github %}")
    _rc("GitHub: {{ contact_github }}")
    _rc("{%p endif %}")

    for row in header_table.rows:
        row.cells[0].width = Cm(8.0)
        row.cells[1].width = Cm(8.5)
    _remove_borders(header_table)

    # ─── 2. Kurzprofil ─────────────────────────────────────────────────────
    doc.add_paragraph("{%p if kurzprofil_saetze %}")
    doc.add_heading("Kurzprofil", level=2)
    doc.add_paragraph("{%p for satz in kurzprofil_saetze %}")
    satz_para = doc.add_paragraph("{{ satz }}")
    satz_para.paragraph_format.space_after = Pt(2)
    satz_para.paragraph_format.space_before = Pt(0)
    doc.add_paragraph("{%p endfor %}")
    doc.add_paragraph("{%p endif %}")

    # ─── 4. Schlüsselkompetenzen (Kategorie + Items) ───────────────────────
    # Tabelle: Kategorie-Label (links, 1/3) | Bullet-Liste der Items (rechts, 2/3)
    sk_num_id = _add_spiegelstrich_numbering(doc)
    doc.add_paragraph("{%p if schluesselkompetenzen_kategorien %}")
    doc.add_heading("Schlüsselkompetenzen", level=2)
    sk_table = doc.add_table(rows=3, cols=2)
    sk_table.style = "Table Grid"
    _clear_and_set(
        sk_table.rows[0].cells[0],
        "{%tr for kat in schluesselkompetenzen_kategorien %}",
    )
    _clear_and_set(sk_table.rows[1].cells[0], "{{ kat.label }}")
    right_cell = sk_table.rows[1].cells[1]
    _clear_and_set(right_cell, "{%p for item in kat.eintraege %}")
    item_para = right_cell.add_paragraph("{{ item }}")
    _apply_list_numbering(item_para, sk_num_id)
    right_cell.add_paragraph("{%p endfor %}")
    _clear_and_set(sk_table.rows[2].cells[0], "{%tr endfor %}")
    # Spaltenbreiten 1/3 : 2/3
    for row in sk_table.rows:
        row.cells[0].width = Cm(5.5)
        row.cells[1].width = Cm(11.0)
    doc.add_paragraph("{%p endif %}")

    # ─── 5. IT-Know-How ────────────────────────────────────────────────────
    # Wissensgebiete in Reihenfolge der Aneignung; pro Gebiet ein Heading,
    # optional ein Halbsatz „Architekturstil" und eine Tabelle mit den
    # Subkategorien (Sprache, Framework, Persistenz, …).
    doc.add_heading("IT-Know-How", level=2)
    doc.add_paragraph("{%p for wg in wissensgebiete %}")
    wg_heading = doc.add_heading("{{ wg.titel }}", level=3)
    run_as = wg_heading.add_run(
        "{% if wg.architekturstil %}  –  {{ wg.architekturstil }}{% endif %}"
    )
    run_as.bold = False

    wg_table = doc.add_table(rows=3, cols=2)
    wg_table.style = "Table Grid"
    _clear_and_set(wg_table.rows[0].cells[0], "{%tr for kat in wg.kategorien %}")
    _clear_and_set(wg_table.rows[1].cells[0], "{{ kat.typ }}")
    _clear_and_set(wg_table.rows[1].cells[1], "{{ kat.items_str }}")
    _clear_and_set(wg_table.rows[2].cells[0], "{%tr endfor %}")
    for row in wg_table.rows:
        row.cells[0].width = Cm(5.5)
        row.cells[1].width = Cm(11.0)
    doc.add_paragraph("{%p endfor %}")

    # ─── 6. Werdegang (Festanstellungen) ───────────────────────────────────
    doc.add_paragraph("{%p if werdegang %}")
    doc.add_page_break()
    doc.add_heading("Beruflicher Werdegang", level=2)
    wd_table = doc.add_table(rows=4, cols=3)
    wd_table.style = "Table Grid"
    for i, label in enumerate(["Zeitraum", "Position", "Arbeitgeber"]):
        cell = wd_table.rows[0].cells[i]
        _clear_and_set(cell, label)
        cell.paragraphs[0].runs[0].bold = True
    _clear_and_set(wd_table.rows[1].cells[0], "{%tr for w in werdegang %}")
    wdr = wd_table.rows[2]
    _clear_and_set(wdr.cells[0], "{{ w.start }}–{{ w.end }}")
    _clear_and_set(wdr.cells[1], "{{ w.titel }}")
    wdr.cells[1].paragraphs[0].paragraph_format.space_after = Pt(6)
    wdr.cells[1].add_paragraph("{{ w.beschreibung }}")
    _clear_and_set(wdr.cells[2], "{{ w.arbeitgeber }}")
    _clear_and_set(wd_table.rows[3].cells[0], "{%tr endfor %}")
    for row in wd_table.rows:
        row.cells[0].width = Cm(3.0)
        row.cells[1].width = Cm(8.5)
        row.cells[2].width = Cm(5.0)
    doc.add_paragraph("{%p endif %}")

    # ─── 7. Projekterfahrung ───────────────────────────────────────────────
    doc.add_page_break()
    doc.add_heading("Projekterfahrung", level=2)
    proj_table = doc.add_table(rows=4, cols=2)
    proj_table.style = "Table Grid"
    for i, label in enumerate(["Zeitraum / Auftraggeber / Rolle", "Projekt"]):
        cell = proj_table.rows[0].cells[i]
        _clear_and_set(cell, label)
        cell.paragraphs[0].runs[0].bold = True
    _clear_and_set(proj_table.rows[1].cells[0], "{%tr for p in projekte %}")
    pr = proj_table.rows[2]
    _clear_and_set(pr.cells[0], "{{ p.start }}–{{ p.end }}")
    pr.cells[0].add_paragraph("{{ p.auftraggeber_label }}")
    pr.cells[0].add_paragraph("{{ p.rolle }}")
    _clear_and_set(pr.cells[1], "{{ p.title }}")
    pr.cells[1].add_paragraph("{{ p.description }}")
    pr.cells[1].add_paragraph("{{ p.achievements_str }}")
    _clear_and_set(proj_table.rows[3].cells[0], "{%tr endfor %}")
    for row in proj_table.rows:
        row.cells[0].width = Cm(5.5)
        row.cells[1].width = Cm(11.0)

    # ─── 8. Ausbildung ─────────────────────────────────────────────────────
    doc.add_page_break()
    doc.add_heading("Ausbildung", level=2)
    aus_table = doc.add_table(rows=4, cols=3)
    aus_table.style = "Table Grid"
    for i, label in enumerate(["Zeitraum", "Abschluss", "Institution"]):
        cell = aus_table.rows[0].cells[i]
        _clear_and_set(cell, label)
        cell.paragraphs[0].runs[0].bold = True
    _clear_and_set(aus_table.rows[1].cells[0], "{%tr for a in ausbildungen %}")
    ar = aus_table.rows[2]
    _clear_and_set(ar.cells[0], "{{ a.periode }}")
    _clear_and_set(ar.cells[1], "{{ a.title }}")
    ar.cells[1].add_paragraph("{{ a.abschluss }}")
    _clear_and_set(ar.cells[2], "{{ a.institution }}")
    _clear_and_set(aus_table.rows[3].cells[0], "{%tr endfor %}")

    # ─── 9. Fortbildung ────────────────────────────────────────────────────
    doc.add_paragraph("{%p if zertifikate %}")
    doc.add_heading("Fortbildung", level=2)
    zert_table = doc.add_table(rows=4, cols=3)
    zert_table.style = "Table Grid"
    for i, label in enumerate(["Jahr", "Titel", "Aussteller"]):
        cell = zert_table.rows[0].cells[i]
        _clear_and_set(cell, label)
        cell.paragraphs[0].runs[0].bold = True
    _clear_and_set(zert_table.rows[1].cells[0], "{%tr for z in zertifikate %}")
    zr = zert_table.rows[2]
    _clear_and_set(zr.cells[0], "{{ z.jahr }}")
    _clear_and_set(zr.cells[1], "{{ z.titel }}")
    _clear_and_set(zr.cells[2], "{{ z.aussteller }}")
    _clear_and_set(zert_table.rows[3].cells[0], "{%tr endfor %}")
    doc.add_paragraph("{%p endif %}")

    # ─── 10. Sprachen ──────────────────────────────────────────────────────
    doc.add_paragraph("{%p if sprachen %}")
    doc.add_page_break()
    doc.add_heading("Sprachen", level=2)
    spr_table = doc.add_table(rows=4, cols=2)
    spr_table.style = "Table Grid"
    for i, label in enumerate(["Sprache", "Level"]):
        cell = spr_table.rows[0].cells[i]
        _clear_and_set(cell, label)
        cell.paragraphs[0].runs[0].bold = True
    _clear_and_set(spr_table.rows[1].cells[0], "{%tr for s in sprachen %}")
    sr = spr_table.rows[2]
    _clear_and_set(sr.cells[0], "{{ s.bezeichnung }}")
    _clear_and_set(sr.cells[1], "{{ s.level }}")
    _clear_and_set(spr_table.rows[3].cells[0], "{%tr endfor %}")
    for row in spr_table.rows:
        row.cells[0].width = Cm(5.5)
        row.cells[1].width = Cm(11.0)
    doc.add_paragraph("{%p endif %}")

    # ─── 11. Publikationen ─────────────────────────────────────────────────
    doc.add_paragraph("{%p if publikationen %}")
    doc.add_heading("Publikationen", level=2)
    pub_table = doc.add_table(rows=4, cols=2)
    pub_table.style = "Table Grid"
    for i, label in enumerate(["Jahr", "Titel"]):
        cell = pub_table.rows[0].cells[i]
        _clear_and_set(cell, label)
        cell.paragraphs[0].runs[0].bold = True
    _clear_and_set(pub_table.rows[1].cells[0], "{%tr for pub in publikationen %}")
    pubr = pub_table.rows[2]
    _clear_and_set(pubr.cells[0], "{{ pub.jahr }}")
    _clear_and_set(pubr.cells[1], "{{ pub.titel }}")
    pubr.cells[1].add_paragraph("{{ pub.beschreibung }}")
    _clear_and_set(pub_table.rows[3].cells[0], "{%tr endfor %}")
    for row in pub_table.rows:
        row.cells[0].width = Cm(2.0)
        row.cells[1].width = Cm(14.5)
    doc.add_paragraph("{%p endif %}")

    # ─── 12. Wissenschaftliche Interessen ──────────────────────────────────
    doc.add_paragraph("{%p if wissenschaftliche_interessen %}")
    doc.add_heading("Wissenschaftliche Interessen", level=2)
    wi_table = doc.add_table(rows=3, cols=1)
    wi_table.style = "Table Grid"
    _clear_and_set(wi_table.rows[0].cells[0], "{%tr for wi in wissenschaftliche_interessen %}")
    _clear_and_set(wi_table.rows[1].cells[0], "{{ wi.stichwort }}")
    _clear_and_set(wi_table.rows[2].cells[0], "{%tr endfor %}")
    doc.add_paragraph("{%p endif %}")

    # ─── 12. Persönliche Daten ─────────────────────────────────────────────
    doc.add_paragraph("{%p if persoenliche_daten_liste %}")
    doc.add_heading("Persönliche Daten", level=2)
    pd_table = doc.add_table(rows=3, cols=2)
    pd_table.style = "Table Grid"
    _clear_and_set(pd_table.rows[0].cells[0], "{%tr for pd in persoenliche_daten_liste %}")
    _clear_and_set(pd_table.rows[1].cells[0], "{{ pd.label }}")
    _clear_and_set(pd_table.rows[1].cells[1], "{{ pd.value }}")
    _clear_and_set(pd_table.rows[2].cells[0], "{%tr endfor %}")
    for row in pd_table.rows:
        row.cells[0].width = Cm(5.5)
        row.cells[1].width = Cm(11.0)
    doc.add_paragraph("{%p endif %}")

    for table in doc.tables:
        _no_row_split(table)
        _set_cell_padding(table)

    # ─── Seitenränder + Header/Footer-Abstände ────────────────────────────
    section = doc.sections[0]
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.header_distance = Cm(0.8)
    section.footer_distance = Cm(0.8)

    # ─── Header ab Seite 2 ────────────────────────────────────────────────
    section.different_first_page_header_footer = True
    hp = section.header.paragraphs[0]
    hp.clear()
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.add_run("{{ person_name }} – ")
    _append_field(hp, 'STYLEREF "Überschrift 2"')

    # ─── Footer ───────────────────────────────────────────────────────────
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.clear()
    ft = footer.add_table(rows=1, cols=3, width=Cm(16.5))
    ft.rows[0].cells[0].width = Cm(6.0)
    ft.rows[0].cells[1].width = Cm(4.5)
    ft.rows[0].cells[2].width = Cm(6.0)
    _remove_borders(ft)

    lp = ft.rows[0].cells[0].paragraphs[0]
    lp.clear()
    lp.paragraph_format.space_before = Pt(0)
    lp.add_run("{{ today_date }}")

    cp = ft.rows[0].cells[1].paragraphs[0]
    cp.clear()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.add_run("Version: {{ filename }}")

    rp = ft.rows[0].cells[2].paragraphs[0]
    rp.clear()
    rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    rp.add_run("Seite ")
    _append_field(rp, "PAGE")
    rp.add_run(" von ")
    _append_field(rp, "NUMPAGES")

    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output))


def _person_node_data(psm: nx.DiGraph[str]) -> dict[str, Any]:
    for _, data in psm.nodes(data=True):
        if data.get("type") == "Person":
            return dict(data)
    return {}


def _build_context(psm: nx.DiGraph[str], profil: Profil, anf: Anforderungen) -> dict[str, Any]:
    # Schlüsselkompetenzen aus dem PSM (zielgruppen-spezifisch geordnet)
    person_node = _person_node_data(psm)
    sk_ordered = person_node.get("schluesselkompetenzen_ordered") or []
    schluesselkompetenzen_kategorien: list[dict[str, Any]] = [
        {
            "key": entry["key"],
            "label": entry["label"],
            "eintraege": [item.replace(" — ", ": ", 1) for item in entry["items"]],
        }
        for entry in sk_ordered
        if entry["key"] != "fuehrungkompetenz"
    ]

    wissensgebiete: list[dict[str, Any]] = []
    for wg in sorted(profil.wissensgebiete, key=lambda w: w.reihenfolge):
        kategorien_str = "; ".join(f"{kat.typ}: {', '.join(kat.items)}" for kat in wg.kategorien)
        wissensgebiete.append(
            {
                "titel": wg.titel,
                "reihenfolge": str(wg.reihenfolge),
                "architekturstil": wg.architekturstil,
                "kategorien_str": kategorien_str,
                "kategorien": [
                    {"typ": kat.typ, "items_str": ", ".join(kat.items)} for kat in wg.kategorien
                ],
            }
        )

    projekte: list[dict[str, Any]] = []
    for p in profil.projekte:
        achievements = "\n".join(f"• {a}" for a in p.achievements)
        # Externer Sektor-Begriff (auftraggeber.extern) hat Vorrang vor
        # dem internen Namen (label), damit der Word-Output extern-tauglich ist
        # ohne dass die interne Datenbasis verändert werden muss.
        if p.auftraggeber:
            auftraggeber_label = (
                p.auftraggeber.extern or p.auftraggeber.label or p.auftraggeber.name
            )
        else:
            auftraggeber_label = ""
        projekte.append(
            {
                "title": p.title,
                "start": _fmt_date(p.start),
                "end": _fmt_date(p.end),
                "auftraggeber_label": auftraggeber_label,
                "rolle": p.rolle,
                "description": p.description,
                "achievements_str": Listing(achievements) if achievements else "",
            }
        )

    ausbildungen: list[dict[str, Any]] = [
        {
            "title": a.title,
            "institution": a.institution,
            "periode": _fmt_date(a.start)
            if a.start == a.end
            else f"{_fmt_date(a.start)}–{_fmt_date(a.end)}",
            "abschluss": a.abschluss,
        }
        for a in profil.ausbildungen
    ]

    werdegang: list[dict[str, Any]] = [
        {
            "titel": w.titel,
            "arbeitgeber": w.arbeitgeber,
            "start": _fmt_date(w.start),
            "end": _fmt_date(w.end),
            "beschreibung": w.beschreibung,
        }
        for w in profil.werdegang
    ]

    zertifikate: list[dict[str, Any]] = [
        {
            "titel": z.titel,
            "aussteller": z.aussteller,
            "jahr": str(z.jahr),
            "url": z.url,
        }
        for z in sorted(profil.zertifikate, key=lambda z: z.jahr, reverse=True)
    ]

    sprachen: list[dict[str, Any]] = [
        {"bezeichnung": s.bezeichnung, "level": s.level} for s in profil.sprachen
    ]

    persoenliche_daten_liste: list[dict[str, str]] = []
    pd = profil.person.persoenlicheDaten
    if pd is not None:
        for label, value in [
            (
                "Geburtsdatum",
                f"{_fmt_geburtstag(pd.geburtsdatum)} in {pd.geburtsort}"
                if pd.geburtsort
                else _fmt_geburtstag(pd.geburtsdatum),
            ),
            ("Staatsangehörigkeit", pd.staatsangehoerigkeit),
            ("Familienstand", pd.familienstand),
            ("Kinder", pd.kinder),
        ]:
            if value:
                persoenliche_daten_liste.append({"label": label, "value": value})

    c = profil.person.contact
    return {
        "person_name": profil.person.name.replace("_", " "),
        "person_title": profil.person.title,
        "person_qualifikation": profil.person.qualifikation,
        "contact_email": c.email if c else "",
        "contact_phone": c.phone if c else "",
        "contact_festnetz": c.festnetz if c else "",
        "contact_strasse": c.strasse if c else "",
        "contact_plz_ort": c.plz_ort if c else "",
        "contact_location": c.location if c else "",
        "contact_linkedin": (c.linkedin or "")
        .replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
        if c
        else "",
        "contact_github": (c.github or "").replace("https://", "").replace("http://", "")
        if c
        else "",
        "kurzprofil_saetze": [
            s.strip() if s.strip().endswith(".") else s.strip() + "."
            for s in (profil.person.kurzprofil or "").split(". ")
            if s.strip()
        ],
        "zielrolle": anf.rolle,
        "schluesselkompetenzen_kategorien": schluesselkompetenzen_kategorien,
        "wissensgebiete": wissensgebiete,
        "projekte": projekte,
        "werdegang": werdegang,
        "ausbildungen": ausbildungen,
        "zertifikate": zertifikate,
        "sprachen": sprachen,
        "publikationen": [
            {"titel": pub.titel, "jahr": str(pub.jahr), "beschreibung": pub.beschreibung or ""}
            for pub in profil.publikationen
        ],
        "wissenschaftliche_interessen": [
            {"stichwort": wi.stichwort} for wi in profil.wissenschaftliche_interessen
        ],
        "persoenliche_daten_liste": persoenliche_daten_liste,
    }


def generate_word_file(
    psm: nx.DiGraph[str],
    profil: Profil,
    anf: Anforderungen,
    output: Path,
    template: Path = DEFAULT_TEMPLATE,
) -> None:
    from datetime import date

    doc = DocxTemplate(str(template))
    context = _build_context(psm, profil, anf)
    context["filename"] = output.name
    context["today_date"] = date.today().strftime("%d.%m.%Y")
    doc.render(context)
    doc.save(str(output))
