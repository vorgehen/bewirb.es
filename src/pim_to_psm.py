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


def _wg_terms(data: dict[str, Any]) -> list[str]:
    """Sammelt Match-Terme aus einem Wissensgebiet-Knoten (Titel + alle Items)."""
    terms: list[str] = [data.get("titel", "")]
    for kat in data.get("kategorien", []) or []:
        terms.extend(kat.get("items", []) or [])
    return [t for t in terms if t]


def transform(pim: nx.DiGraph[str], anf: Anforderungen) -> nx.DiGraph[str]:
    """M2M: annotiert PIM-Graph mit Relevanz-Metadaten und Zielgruppen-Ableitung.

    - Wissensgebiet-Knoten: matched / nice_to_have / relevant (über Substring-
      Vergleich gegen Titel + Subkategorie-Items)
    - Person-Knoten: schluesselkompetenzen_ordered (zielgruppen-spezifisch
      geordnet und umbenannt)
    """
    psm: nx.DiGraph[str] = pim.copy()

    must_lower = [t.lower() for t in anf.must_have]
    nice_lower = [t.lower() for t in anf.nice_to_have]

    for node, data in psm.nodes(data=True):
        node_type = data.get("type")
        if node_type == "Wissensgebiet":
            terms_lower = [t.lower() for t in _wg_terms(data)]
            matched = any(m in t for m in must_lower for t in terms_lower)
            nice = any(n in t for n in nice_lower for t in terms_lower)
            psm.nodes[node]["matched"] = matched
            psm.nodes[node]["nice_to_have"] = nice
            psm.nodes[node]["relevant"] = matched or nice
        elif node_type == "Person":
            sk = data.get("schluesselkompetenzen")
            if sk:
                psm.nodes[node]["schluesselkompetenzen_ordered"] = _ordne_schluesselkompetenzen(
                    sk, anf.zielgruppe
                )

    return psm
