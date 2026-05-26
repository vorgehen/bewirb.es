from __future__ import annotations

from pathlib import Path

import pytest

from src.anonymizer import (
    AnonymizeConfig,
    anonymize_documents,
    anonymize_text,
    collect_files,
    extract_text,
)

pytestmark = pytest.mark.unit


# ─── Standard-Pattern ──────────────────────────────────────────────────────


def test_email_wird_ersetzt() -> None:
    text = "Kontakt: max@beispiel.de und info@firma.com"
    out, audit = anonymize_text(text)
    assert "max@beispiel.de" not in out
    assert "info@firma.com" not in out
    assert "[EMAIL]" in out
    assert any(r.kategorie == "email" for r in audit.replacements)


def test_iban_wird_ersetzt() -> None:
    text = "Konto: DE89 3704 0044 0532 0130 00"
    out, audit = anonymize_text(text)
    assert "[IBAN]" in out
    assert any(r.kategorie == "iban" for r in audit.replacements)


def test_ip_wird_ersetzt() -> None:
    text = "Server: 192.168.1.42"
    out, audit = anonymize_text(text)
    assert "192.168.1.42" not in out
    assert "[IP]" in out


def test_url_wird_ersetzt() -> None:
    text = "Doku: https://intranet.beispiel-bank.de/page"
    out, audit = anonymize_text(text)
    assert "intranet.beispiel-bank.de" not in out
    assert "[URL]" in out


# ─── Konfig-Wörterbuch ─────────────────────────────────────────────────────


def test_replace_dict_aus_config() -> None:
    config = AnonymizeConfig(
        replace={
            "Beispiel-Bank AG": "[Finanzinstitut]",
            "Max Mustermann": "[Projektleiter]",
        }
    )
    text = "Bei der Beispiel-Bank AG arbeitete Max Mustermann als Architekt."
    out, audit = anonymize_text(text, config)
    assert "Beispiel-Bank AG" not in out
    assert "Max Mustermann" not in out
    assert "[Finanzinstitut]" in out
    assert "[Projektleiter]" in out


def test_replace_dict_laengste_keys_zuerst() -> None:
    """Wenn 'Beispiel-Bank Frankfurt' und 'Beispiel-Bank' beide konfiguriert sind,
    muss der längere Key zuerst ersetzt werden."""
    config = AnonymizeConfig(
        replace={
            "Beispiel-Bank": "[Bank]",
            "Beispiel-Bank Frankfurt": "[Bank Frankfurt]",
        }
    )
    text = "Standort: Beispiel-Bank Frankfurt"
    out, _ = anonymize_text(text, config)
    assert "[Bank Frankfurt]" in out
    assert "[Bank] Frankfurt" not in out


def test_public_domain_wird_geschuetzt() -> None:
    """Begriffe in public_domain dürfen nicht ersetzt werden, auch wenn
    ein Konfig-Pattern sie matchen würde."""
    config = AnonymizeConfig(
        replace={"BaFin": "[Behörde]"},
        public_domain=["BaFin"],
    )
    text = "Die BaFin-Anforderungen sind regulatorisch."
    out, audit = anonymize_text(text, config)
    assert "BaFin" in out  # bleibt
    assert "[Behörde]" not in out


def test_public_domain_taucht_im_audit_auf() -> None:
    config = AnonymizeConfig(public_domain=["BaFin", "DORA"])
    text = "BaFin-Regulierung unter DORA"
    _, audit = anonymize_text(text, config)
    assert "BaFin" in audit.public_domain_skipped
    assert "DORA" in audit.public_domain_skipped


# ─── Konfig-Pattern ────────────────────────────────────────────────────────


def test_eigene_patterns_aus_config() -> None:
    config = AnonymizeConfig(patterns=[{"pattern": r"\bANON-\d{4}\b", "replacement": "[Ticket]"}])
    text = "Siehe ANON-1234 und ANON-9876."
    out, _ = anonymize_text(text, config)
    assert "ANON-1234" not in out
    assert "ANON-9876" not in out
    assert out.count("[Ticket]") == 2


# ─── Konfig-Load ───────────────────────────────────────────────────────────


def test_config_load_from_yaml(tmp_path: Path) -> None:
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text(
        """
replace:
  "Foo GmbH": "[Firma]"
public_domain:
  - BaFin
patterns:
  - pattern: '\\bT-\\d+\\b'
    replacement: '[T-Code]'
""",
        encoding="utf-8",
    )
    cfg = AnonymizeConfig.load(cfg_file)
    assert cfg.replace["Foo GmbH"] == "[Firma]"
    assert "BaFin" in cfg.public_domain
    assert cfg.patterns[0]["pattern"] == r"\bT-\d+\b"


def test_config_load_missing_file_returns_default(tmp_path: Path) -> None:
    cfg = AnonymizeConfig.load(tmp_path / "does_not_exist.yaml")
    assert cfg.replace == {}
    assert cfg.public_domain == []


def test_config_load_none_returns_default() -> None:
    cfg = AnonymizeConfig.load(None)
    assert cfg.replace == {}


# ─── Audit-Log ─────────────────────────────────────────────────────────────


def test_audit_count_summiert_wiederholte_treffer() -> None:
    text = "a@x.de und b@y.de und c@z.de"
    _, audit = anonymize_text(text)
    email_replacements = [r for r in audit.replacements if r.kategorie == "email"]
    # Drei verschiedene Emails — drei Einträge, jeder mit count=1
    assert len(email_replacements) == 3


def test_audit_count_summiert_gleiches_match_mehrfach() -> None:
    text = "Email max@x.de, dann nochmal max@x.de"
    _, audit = anonymize_text(text)
    rep = next(r for r in audit.replacements if r.original == "max@x.de")
    assert rep.count == 2


def test_audit_format_enthaelt_kategorien() -> None:
    text = "Kontakt: max@x.de, IP 1.2.3.4"
    _, audit = anonymize_text(text)
    out = audit.format()
    assert "email" in out
    assert "ipv4" in out


# ─── Dokument-Lesen ───────────────────────────────────────────────────────


def _make_docx(path: Path, paragraphs: list[str]) -> None:
    from docx import Document

    d = Document()
    for p in paragraphs:
        d.add_paragraph(p)
    d.save(str(path))


def test_extract_text_aus_docx(tmp_path: Path) -> None:
    docx = tmp_path / "doc.docx"
    _make_docx(docx, ["Zeile 1", "Zeile 2"])
    text = extract_text(docx)
    assert "Zeile 1" in text
    assert "Zeile 2" in text


def test_extract_text_aus_txt(tmp_path: Path) -> None:
    txt = tmp_path / "doc.txt"
    txt.write_text("Plain Text Inhalt", encoding="utf-8")
    assert "Plain Text Inhalt" in extract_text(txt)


def test_collect_files_recurses_directory(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    a = tmp_path / "a.docx"
    b = sub / "b.txt"
    _make_docx(a, ["A"])
    b.write_text("B", encoding="utf-8")
    files = collect_files([tmp_path])
    assert a in files and b in files


def test_collect_files_empty_dir_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        collect_files([tmp_path])


# ─── End-to-End ────────────────────────────────────────────────────────────


def test_anonymize_documents_e2e(tmp_path: Path) -> None:
    docx = tmp_path / "report.docx"
    _make_docx(
        docx,
        [
            "Kontakt: max@beispiel.de",
            "Konto bei der Beispiel-Bank AG",
            "Doku: https://intern.example.de/wiki",
        ],
    )
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text('replace:\n  "Beispiel-Bank AG": "[Bank]"\n', encoding="utf-8")
    text, audit = anonymize_documents([docx], cfg_file)
    assert "max@beispiel.de" not in text
    assert "Beispiel-Bank AG" not in text
    assert "intern.example.de" not in text
    assert "[EMAIL]" in text and "[Bank]" in text and "[URL]" in text
    assert any(r.original == "Beispiel-Bank AG" for r in audit.replacements)
