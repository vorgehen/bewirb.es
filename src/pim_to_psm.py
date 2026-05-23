from __future__ import annotations

import networkx as nx

from src.data_loader import Anforderungen


def transform(pim: nx.DiGraph[str], anf: Anforderungen) -> nx.DiGraph[str]:
    """M2M: annotiert PIM-Graph mit Relevanz-Metadaten aus den Anforderungen."""
    psm: nx.DiGraph[str] = pim.copy()

    must_lower = {t.lower() for t in anf.must_have}
    nice_lower = {t.lower() for t in anf.nice_to_have}

    for node, data in psm.nodes(data=True):
        if data.get("type") == "Technologiekompetenz":
            name_lower = data.get("name", "").lower()
            psm.nodes[node]["matched"] = name_lower in must_lower
            psm.nodes[node]["nice_to_have"] = name_lower in nice_lower
            psm.nodes[node]["relevant"] = (
                psm.nodes[node]["matched"] or psm.nodes[node]["nice_to_have"]
            )

    return psm
