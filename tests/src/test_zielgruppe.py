from __future__ import annotations

import pytest

from src.zielgruppe import (
    DEFAULT_STIL,
    KATEGORIEN,
    LABEL_MAP,
    PROMINENZ,
    kategorien_fuer_zielgruppe,
    resolve_stil,
)

pytestmark = pytest.mark.unit


def test_kategorien_konstant() -> None:
    assert set(KATEGORIEN) == {
        "methodenkompetenz",
        "fachkompetenz",
        "fuehrungkompetenz",
        "programmierparadigmen",
    }


def test_label_map_vollstaendig() -> None:
    """Jede Zielgruppe hat ein Label für jede der vier Kategorien."""
    for stil, labels in LABEL_MAP.items():
        assert set(labels.keys()) == set(KATEGORIEN), f"{stil} hat unvollständiges Mapping"
        for kat, label in labels.items():
            assert label, f"{stil}.{kat} hat leeres Label"


def test_prominenz_vollstaendig() -> None:
    """Jede Zielgruppe ordnet alle vier Kategorien (keine fehlt, keine doppelt)."""
    for stil, order in PROMINENZ.items():
        assert set(order) == set(KATEGORIEN), f"{stil} Prominenz unvollständig"
        assert len(order) == 4


def test_label_map_und_prominenz_haben_gleiche_zielgruppen() -> None:
    assert set(LABEL_MAP.keys()) == set(PROMINENZ.keys())


def test_resolve_stil_kennt_alle_grammatik_werte() -> None:
    """Alle Werte aus Angebotsstil (requirements.tx) sind abgedeckt."""
    stile = ("Behoerde", "Consultant", "StartUp", "Wissenschaftlich", "Standard", "AIGovernance")
    for stil in stile:
        assert resolve_stil(stil) == stil


def test_resolve_stil_fallback_bei_leer_oder_unbekannt() -> None:
    assert resolve_stil("") == DEFAULT_STIL
    assert resolve_stil(None) == DEFAULT_STIL
    assert resolve_stil("Lifestyle") == DEFAULT_STIL


def test_kategorien_fuer_zielgruppe_returns_labelled_pairs() -> None:
    pairs = kategorien_fuer_zielgruppe("Behoerde")
    assert len(pairs) == 4
    # Erste Kategorie laut Plan: fachkompetenz
    assert pairs[0] == ("fachkompetenz", "Fachkompetenz")


def test_kategorien_behoerde_priorisiert_fachkompetenz() -> None:
    pairs = kategorien_fuer_zielgruppe("Behoerde")
    keys = [k for k, _ in pairs]
    assert keys[0] == "fachkompetenz"
    assert keys[1] == "methodenkompetenz"


def test_kategorien_konsultant_label_branchenexpertise() -> None:
    pairs = kategorien_fuer_zielgruppe("Consultant")
    fach = next(label for k, label in pairs if k == "fachkompetenz")
    assert fach == "Branchenexpertise"


def test_kategorien_fallback_standard_wenn_leer() -> None:
    standard = kategorien_fuer_zielgruppe("Standard")
    fallback = kategorien_fuer_zielgruppe("")
    assert standard == fallback


def test_programmierparadigmen_immer_am_ende() -> None:
    """Senior-Geste — in allen Stilen rangieren Paradigmen zuletzt."""
    for stil, order in PROMINENZ.items():
        assert order[-1] == "programmierparadigmen", f"{stil} hat Paradigmen nicht am Ende"
