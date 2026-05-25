# Profile Generator (bewirb.es)

**Bewerbungs-Lifecycle-Tool — Profile pflegen und Bewerbungen ableiten.**

Dieses Repository ist gleichzeitig ein **Principal-Level-Architektur-Showcase**:
vollständige ARC42-Dokumentation, Architecture Decision Records und eine
[COMPETENCIES.md](COMPETENCIES.md), die die abstrahierten Kernkompetenzen hinter
dem System beschreibt.

> *Die Invarianten bleiben. Die Werkzeuge werden besser.*

---

## Was es ist

Kein Ein-Schritt-Generator, sondern ein **Lifecycle-Tool mit zwei gleichwertigen Aktivitäten**:

```
╔══════════════════════════════╗   ╔══════════════════════════════╗
║  PFLEGEN (kontinuierlich)    ║   ║  BEWERBEN (pro Angebot)      ║
║                              ║   ║                              ║
║  Import → Vervollständigen   ║   ║  Advisory → Positionieren    ║
║  Anreichern → Anonymisieren  ║   ║  Zielgruppe → Generieren     ║
╚══════════════╤═══════════════╝   ╚══════════════╤═══════════════╝
               │                                  │
               └──────────┬───────────────────────┘
                          ↓
                  .profile + Knowledge Layer
                  (gemeinsamer Zustand)
```

Beide Aktivitäten lesen und schreiben auf denselben gemeinsamen Zustand und
informieren sich gegenseitig: *Pflegen* liefert den Rohstoff, *Bewerben* zeigt
was beim Pflegen fehlt oder besser formuliert werden muss.

---

## Kernprinzipien

| Prinzip | Rolle im Projekt |
|---|---|
| **DDD** — Domain-Driven Design | Fundament: Ubiquitous Language, Bounded Contexts, Aggregates |
| **MDD** — Model-Driven Development | Drei TextX-DSLs → NetworkX-Graph → M2M/M2T-Transformationen |
| **TDD** — Test-Driven Development | Tests parallel zur Implementierung, CI bei jedem Push |

→ Ausführlich: [COMPETENCIES.md](COMPETENCIES.md)

---

## Stand & Roadmap

### M1 — Abgeschlossen
Repository, ARC42-Dokumentation, TextX-Grammatiken, Core-Pipeline
(Markdown + Word Generator, Extractor, 87 Tests).

### M2 — In Arbeit: Lifecycle-Tool-MVP

```
7.5 ✓ Knowledge Layer (Stufe 1, handgefertigte YAML-Daten)
7.6 ✓ Knowledge Layer als DSL (grammar/knowledge.tx, ADR-012)
8   ◔ Metamodell-Erweiterung (Persönliche Daten, Sprachen, Zertifikate,
        Werdegang, Schlüsselkompetenzen, Zielgruppe — in Arbeit)
9     Import-Tool (.docx → .profile DSL)
10    Datenbasis vervollständigen
8a    Advisory Layer (Bewerbungsempfehlung, Portfolio-Scan)
11    KI-Anreicherung (Artefakte + Web-Recherche)
11a   Anonymisierungs-Utility (NDA-sichere Preprocessing-Pipeline)
```

**M2 fertig wenn:** Advisory-Portfolio-Scan über mehrere Angebote läuft,
und das erste angereicherte Profil ist versendet.

### M3 — Geplant: Intelligence & Positioning
AI-Evaluator-Simulation, Agent-Ready Output (JSON-LD für AI-Recruiter-Bots),
Style Learning aus Nutzer-Korrekturen, AI Governance als erstklassige
Kompetenz im Metamodell.

### M4 — Geplant: Web-App, HTML-Output & Multi-User

**Eigene Web-Oberfläche** für den gesamten Lifecycle (Skeleton bereits unter `web/`):
- FastAPI-Backend + Monaco-Editor für direkte `.profile`/`.req`-Bearbeitung
- HTML-Generator als drittes Ausgabeformat — responsive, druckbar,
  als Profillink teilbar (zeitlich begrenzte Sichtbarkeit)
- Live-Preview während der Bearbeitung

**Multi-User-Architektur:**
- Pro-Nutzer-Datenisolation: jeder hat eigenen `.profile`, eigenen `.style`,
  eigene `corrections/`-Korrektur-Historie
- Eigene Stil-Präferenzen als portable `.style`-Datei (exportierbar, DSGVO-Portabilität)
- Opt-in Community-Pool: anonymisierte **Stil-Muster** aus Korrekturen
  (nicht Profilinhalt) fließen in einen gemeinsamen Knowledge Layer
- Strikte Trennung von persönlichem und universellem Wissen (siehe Plan,
  Querschnittsaspekt *Datenstrategie & Kollektives Lernen*)

---

## Architektur

```
grammar/profile.tx       ← M2-Metamodell für die Datenbasis
grammar/requirements.tx  ← M2-Metamodell für Stellenanforderungen
grammar/knowledge.tx     ← M2-Metamodell für Knowledge Layer (Phase 7.6, ADR-012)
        │
        ▼ codegen/codegen.py
src/models.py (auto-generiert)
        │
data/<name>/<name>.profile  ×  job.req  ×  knowledge/*.knowledge
        │
        ▼ src/pim_to_psm.py (M2M: Graph-Transformation)
PSM (maßgeschneidertes Profil)
        │
   ┌────┼────┐
   ▼    ▼    ▼
Markdown Word HTML (M4)
```

Vollständige Architekturdokumentation: [docs/arc42/](docs/arc42/)
Architecture Decision Records: [docs/adr/](docs/adr/)

---

## Schnellstart

```powershell
# Umgebung einrichten
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # ANTHROPIC_API_KEY eintragen

# Codegen (nach jeder Grammatik-Änderung)
python codegen/codegen.py

# Profil generieren (mit anonymisiertem Demo-Profil)
python scripts/generate.py data/example/example.profile data/example/example_job.req

# Word-Vorlage initial erstellen
python scripts/create_template.py

# Word-Profil generieren
python scripts/generate.py data/example/example.profile data/example/example_job.req `
    --format word --output mein_profil.docx
```

---

## Tests

```powershell
# Schnelle Unit-Tests (kein API-Key nötig)
pytest tests/ -m "not integration and not eval"

# Mit Claude-API (benötigt ANTHROPIC_API_KEY)
pytest tests/ -m integration
```

Aktuell: **87 Unit-Tests grün**.

---

## Datenhoheit & Anonymisierung

- Persönliche `.profile`- und `.req`-Dateien gehören **nicht** ins Repo
  — `.gitignore` schützt sie aktiv
- `data/example/` enthält nur anonymisierte Demo-Daten
- `arbeitsdokumente/` ist gitignored (Quelldokumente, Auftraggeber-NDA-Material)
- `src/models.py` und `src/graph_schema.py` sind **auto-generiert** von
  `codegen/codegen.py` — nicht manuell bearbeiten
- Alle Claude-API-Aufrufe laufen über Prompt-Templates in `prompts/*.md`

Phase 11a (in der Roadmap) ergänzt eine dreistufige Anonymisierungs-Pipeline
für Kundendokumente — lokale NER + optionales LLM-Postprocessing — bevor
diese in die Anreicherung einfließen.

---

## Entwickelt mit

- [TextX](https://textx.github.io/textX/) — DSL-Framework (Python-Äquivalent zu Xtext)
- [NetworkX](https://networkx.org/) — Graph-Datenstruktur und Traversierung
- [Pydantic](https://docs.pydantic.dev/) — typisierte Domain-Modelle aus Codegen
- [Claude API](https://docs.anthropic.com/) — Extraktion, Anreicherung, Advisory
- [python-docx / docxtpl](https://python-docx.readthedocs.io/) — Word-Generierung
- [FastAPI](https://fastapi.tiangolo.com/) — Web-API (M4)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) — Dokumentation

