from __future__ import annotations

import networkx as nx

from src.data_loader import Profil


def build_graph(profil: Profil) -> nx.DiGraph[str]:
    g: nx.DiGraph[str] = nx.DiGraph()

    person_id = f"Person:{profil.person.name}"
    person_attrs: dict[str, object] = {
        "type": "Person",
        "name": profil.person.name,
        "title": profil.person.title,
        "kurzprofil": profil.person.kurzprofil,
    }
    sk = profil.schluesselkompetenzen
    if sk is not None:
        person_attrs["schluesselkompetenzen"] = {
            "methodenkompetenz": list(sk.methodenkompetenz),
            "fachkompetenz": list(sk.fachkompetenz),
            "fuehrungkompetenz": list(sk.fuehrungkompetenz),
            "programmierparadigmen": list(sk.programmierparadigmen),
        }
    g.add_node(person_id, **person_attrs)

    for wg in profil.wissensgebiete:
        wg_id = f"Wissensgebiet:{wg.name}"
        g.add_node(
            wg_id,
            type="Wissensgebiet",
            name=wg.name,
            titel=wg.titel,
            reihenfolge=wg.reihenfolge,
            architekturstil=wg.architekturstil,
            kategorien=[{"typ": kat.typ, "items": list(kat.items)} for kat in wg.kategorien],
        )

    for projekt in profil.projekte:
        proj_id = f"Projekterfahrung:{projekt.name}"
        g.add_node(
            proj_id,
            type="Projekterfahrung",
            name=projekt.name,
            title=projekt.title,
            start=projekt.start,
            end=projekt.end,
            rolle=projekt.rolle,
        )
        g.add_edge(person_id, proj_id, rel="hat_projekt")
        for wg in projekt.uses:
            g.add_edge(proj_id, f"Wissensgebiet:{wg.name}", rel="uses")

    for ausb in profil.ausbildungen:
        ausb_id = f"Ausbildung:{ausb.name}"
        g.add_node(
            ausb_id,
            type="Ausbildung",
            name=ausb.name,
            title=ausb.title,
            institution=ausb.institution,
            start=ausb.start,
            end=ausb.end,
        )
        g.add_edge(person_id, ausb_id, rel="hat_ausbildung")

    return g
