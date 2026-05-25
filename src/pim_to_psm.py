from __future__ import annotations

from typing import Any

import networkx as nx

from src.data_loader import Anforderungen
from src.zielgruppe import kategorien_fuer_zielgruppe


def _ordne_schluesselkompetenzen(
    sk: dict[str, list[str]], zielgruppe: str | None
) -> list[dict[str, Any]]:
    """Ordnet die fünf Kategorien gemäß Zielgruppe und benennt sie um.

    Leere Kategorien werden ausgelassen — Reihenfolge folgt PROMINENZ[stil].
    """
    ordered: list[dict[str, Any]] = []
    for key, label in kategorien_fuer_zielgruppe(zielgruppe):
        items = sk.get(key, [])
        if items:
            ordered.append({"key": key, "label": label, "items": items})
    return ordered


def transform(pim: nx.DiGraph[str], anf: Anforderungen) -> nx.DiGraph[str]:
    """M2M: annotiert PIM-Graph mit Relevanz-Metadaten und Zielgruppen-Ableitung.

    - Technologiekompetenz-Knoten: matched / nice_to_have / relevant
    - Person-Knoten: schluesselkompetenzen_ordered (zielgruppen-spezifisch
      geordnet und umbenannt)
    """
    psm: nx.DiGraph[str] = pim.copy()

    must_lower = {t.lower() for t in anf.must_have}
    nice_lower = {t.lower() for t in anf.nice_to_have}

    for node, data in psm.nodes(data=True):
        node_type = data.get("type")
        if node_type == "Technologiekompetenz":
            name_lower = data.get("name", "").lower()
            psm.nodes[node]["matched"] = name_lower in must_lower
            psm.nodes[node]["nice_to_have"] = name_lower in nice_lower
            psm.nodes[node]["relevant"] = (
                psm.nodes[node]["matched"] or psm.nodes[node]["nice_to_have"]
            )
        elif node_type == "Person":
            sk = data.get("schluesselkompetenzen")
            if sk:
                psm.nodes[node]["schluesselkompetenzen_ordered"] = _ordne_schluesselkompetenzen(
                    sk, anf.zielgruppe
                )

    return psm
