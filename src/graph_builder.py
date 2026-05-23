from __future__ import annotations

import networkx as nx

from src.data_loader import Profil


def build_graph(profil: Profil) -> nx.DiGraph[str]:
    g: nx.DiGraph[str] = nx.DiGraph()

    person_id = f"Person:{profil.person.name}"
    g.add_node(
        person_id,
        type="Person",
        name=profil.person.name,
        title=profil.person.title,
    )

    for tech in profil.technologien:
        tech_id = f"Technologiekompetenz:{tech.name}"
        g.add_node(
            tech_id,
            type="Technologiekompetenz",
            name=tech.name,
            category=tech.category,
            proficiency=tech.proficiency,
            years=tech.years,
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
        for tech in projekt.uses:
            g.add_edge(proj_id, f"Technologiekompetenz:{tech.name}", rel="uses")

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
