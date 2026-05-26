from __future__ import annotations

from pathlib import Path

import pytest

from src.advisor import GapType, classify_gap, evaluate_offer, scan_offers
from src.data_loader import Anforderungen, load_profile
from src.knowledge_loader import KnowledgeBase, load_knowledge_base

pytestmark = pytest.mark.unit


EXAMPLE_PROFILE = Path(__file__).parent.parent.parent / "data" / "example" / "example.profile"


@pytest.fixture(scope="module")
def kb() -> KnowledgeBase:
    return load_knowledge_base()


@pytest.fixture(scope="module")
def profil() -> object:
    return load_profile(EXAMPLE_PROFILE)


# ─── classify_gap ──────────────────────────────────────────────────────────


def test_classify_artikulation_gap(profil: object, kb: KnowledgeBase) -> None:
    """example.profile hat 'Microservices' im Schluesselkompetenzen-Text aber
    keinen eigenständigen technology-Eintrag mit dem Namen."""
    # example.profile hat eine Technology mit name="Microservices" — also testen
    # wir hier einen anderen Begriff der im Text vorkommt aber nicht als ID
    g = classify_gap("Modellgetriebene Entwicklung", profil, kb)  # type: ignore[arg-type]
    assert g.type == GapType.ARTIKULATION


def test_classify_erfahrungs_gap_for_known_taxonomy_tech(profil: object, kb: KnowledgeBase) -> None:
    """Eine Tech die im Knowledge Layer ist aber nicht im Profil-Text."""
    # 'Quarkus' ist in der Taxonomie aber nicht im example.profile
    # (keine Tech, kein Keyword, kein Schluesselkompetenz-Eintrag)
    g = classify_gap("Quarkus", profil, kb)  # type: ignore[arg-type]
    assert g.type in (GapType.ERFAHRUNG, GapType.ZERTIFIZIERUNG)
    assert g.schliessbar is True


def test_classify_strukturelle_gap_for_unknown_tech(profil: object, kb: KnowledgeBase) -> None:
    g = classify_gap("ObsoleteTechXYZ_unknown", profil, kb)  # type: ignore[arg-type]
    assert g.type == GapType.STRUKTURELL
    assert g.schliessbar is False


# ─── evaluate_offer ────────────────────────────────────────────────────────


def test_evaluate_score_for_full_match(profil: object, kb: KnowledgeBase) -> None:
    anf = Anforderungen(must_have=["Java"], rolle="Test")
    r = evaluate_offer(profil, anf, kb)  # type: ignore[arg-type]
    assert r.score == 1.0
    assert "Java" in r.matched_must_have
    assert r.gaps == []


def test_evaluate_score_for_zero_match(profil: object, kb: KnowledgeBase) -> None:
    anf = Anforderungen(must_have=["Cobol", "Fortran"], rolle="Test")
    r = evaluate_offer(profil, anf, kb)  # type: ignore[arg-type]
    assert r.score == 0.0
    assert len(r.gaps) == 2
    assert all(g.type == GapType.STRUKTURELL for g in r.gaps)


def test_evaluate_recommendation_strings(profil: object, kb: KnowledgeBase) -> None:
    """Verdict-Strings sind die definierten drei Varianten."""
    valid = {"✓ Bewerbung empfohlen", "⚠ bedingt", "✗ nicht empfohlen"}
    for must in (["Java"], ["Java", "Cobol"], ["Cobol", "Fortran"]):
        anf = Anforderungen(must_have=must, rolle="Test")
        r = evaluate_offer(profil, anf, kb)  # type: ignore[arg-type]
        assert r.empfehlung in valid


def test_evaluate_structural_gap_blocks_empfehlung(profil: object, kb: KnowledgeBase) -> None:
    """Sobald eine strukturelle Lücke da ist, ist Empfehlung immer 'nicht empfohlen'."""
    anf = Anforderungen(must_have=["Java", "ObsoleteUnknownTech_x"], rolle="Test")
    r = evaluate_offer(profil, anf, kb)  # type: ignore[arg-type]
    assert r.empfehlung == "✗ nicht empfohlen"


def test_evaluate_alias_resolution(profil: object, kb: KnowledgeBase) -> None:
    """Wenn must_have 'JVM' fordert und das Profil 'Java' hat, soll matchen."""
    anf = Anforderungen(must_have=["JVM"], rolle="Test")
    r = evaluate_offer(profil, anf, kb)  # type: ignore[arg-type]
    assert "JVM" in r.matched_must_have
    assert r.score == 1.0


# ─── Portfolio-Scan ────────────────────────────────────────────────────────


def test_scan_empty_dir_returns_empty(tmp_path: Path) -> None:
    result = scan_offers(EXAMPLE_PROFILE, tmp_path)
    assert result.entries == []
    assert result.recurring_gaps == []


def test_scan_ranks_by_score(tmp_path: Path) -> None:
    # Drei Test-Req-Dateien mit unterschiedlichem Match
    (tmp_path / "good.req").write_text(
        'requirements Good { rolle: "X" must_have: ["Java"] }', encoding="utf-8"
    )
    (tmp_path / "bad.req").write_text(
        'requirements Bad { rolle: "X" must_have: ["Cobol", "Fortran", "AssemblyVAX"] }',
        encoding="utf-8",
    )
    (tmp_path / "mid.req").write_text(
        'requirements Mid { rolle: "X" must_have: ["Java", "Cobol"] }', encoding="utf-8"
    )
    result = scan_offers(EXAMPLE_PROFILE, tmp_path)
    assert len(result.entries) == 3
    # Absteigend nach Score sortiert
    scores = [e.score for e in result.entries]
    assert scores == sorted(scores, reverse=True)
    assert result.entries[0].file == "good.req"


def test_voraussetzungen_filter_aus_score(profil: object, kb: KnowledgeBase) -> None:
    """Formale Voraussetzungen (Sprache, Staatsangehörigkeit, etc.) fließen
    nicht in den Score, sondern werden separat als voraussetzungen gelistet.
    """
    from src.data_loader import Anforderungen

    anf = Anforderungen(
        rolle="Test",
        must_have=[
            "Java",  # technische Anforderung
            "Deutsch C1 GER",  # Sprache
            "EU/EWR-Staatsangehörigkeit",  # Staatsangehörigkeit
            "Mindestens 5 Jahre Berufserfahrung",  # pauschal
            "Hochschulabschluss in Informatik",  # akademisch
        ],
    )
    r = evaluate_offer(profil, anf, kb)  # type: ignore[arg-type]
    assert len(r.voraussetzungen) == 4
    kategorien = {kat for _, kat in r.voraussetzungen}
    assert "Sprachkenntnisse" in kategorien
    assert "Staatsangehörigkeit" in kategorien
    assert "Berufserfahrung-pauschal" in kategorien
    assert "Akademischer Abschluss" in kategorien
    # Java ist die einzige echte must_have → 100%
    assert r.score == 1.0
    assert r.matched_must_have == ["Java"]


def test_tech_anforderung_wird_nicht_als_voraussetzung_klassifiziert(
    profil: object, kb: KnowledgeBase
) -> None:
    """5 Jahre Java-Erfahrung enthält 'Java' → kein soft-requirement."""
    from src.data_loader import Anforderungen

    anf = Anforderungen(rolle="Test", must_have=["Mindestens 5 Jahre Erfahrung mit Java"])
    r = evaluate_offer(profil, anf, kb)  # type: ignore[arg-type]
    assert r.voraussetzungen == []
    assert "Mindestens 5 Jahre Erfahrung mit Java" in r.matched_must_have


def test_scan_detects_recurring_gaps(tmp_path: Path) -> None:
    """Wenn 'Cobol' in mehreren Angeboten als must_have fehlt, taucht es in recurring_gaps."""
    (tmp_path / "a.req").write_text(
        'requirements A { rolle: "X" must_have: ["Cobol"] }', encoding="utf-8"
    )
    (tmp_path / "b.req").write_text(
        'requirements B { rolle: "X" must_have: ["Cobol", "Fortran"] }', encoding="utf-8"
    )
    result = scan_offers(EXAMPLE_PROFILE, tmp_path)
    terms = [term for term, _ in result.recurring_gaps]
    assert "Cobol" in terms
