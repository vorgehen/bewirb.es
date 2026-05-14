# Profile Generator

**MDA-basierter Profil-Generator für Freiberufler-Bewerbungen**

Ausschreibungstext rein → maßgeschneidertes Word + PDF + HTML-Profil raus.

Dieses Repository ist gleichzeitig ein **Principal-Level-Architektur-Showcase**: vollständige ARC42-Dokumentation, Architecture Decision Records und eine `COMPETENCIES.md`, die die abstrahierten Kernkompetenzen hinter dem System beschreibt.

---

## Kernprinzipien

| Prinzip | Rolle im Projekt |
|---|---|
| **DDD** — Domain-Driven Design | Fundament: Ubiquitous Language, Bounded Contexts, Aggregates |
| **MDD** — Model-Driven Development | Zwei TextX-DSLs → NetworkX-Graph → M2M/M2T-Transformationen |
| **TDD** — Test-Driven Development | Tests parallel zur Implementierung, CI bei jedem Push |
| **AISE** — AI-Supported SW Engineering | KI im Entwicklungsprozess: Code, Docs, Tests, Review |

→ Ausführlich: [COMPETENCIES.md](COMPETENCIES.md)

---

## Schnellstart

```powershell
# Umgebung einrichten
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # ANTHROPIC_API_KEY eintragen

# Profil generieren (mit eigenen Daten)
python generate_profile.py --profile data/mein.profile --req data/jobs/ausschreibung.req

# Dokumentation bauen
python scripts/build_docs.py
```

---

## Architektur

```
grammar/profile.tx + requirements.tx   ← M2 Metamodelle
        │
        ▼ codegen/codegen.py
src/models.py (auto-generiert)
        │
data/mein.profile (PIM)  ×  job.req (Anforderungen)
        │
        ▼ src/pim_to_psm.py (M2M: Graph + Claude API)
job_tailored.profile (PSM)
        │
   ┌────┼────┐
   ▼    ▼    ▼
Word   HTML  Markdown
```

Vollständige Architekturdokumentation: [docs/arc42/](docs/arc42/)

---

## Multi-User

Das Tool ist daten-agnostisch. Eigene Daten einbringen:
```powershell
python generate_profile.py --profile C:\meine-daten\ich.profile --req job.req
```

---

## Entwickelt mit

- [TextX](https://textx.github.io/textX/) — DSL-Framework (Python-Äquivalent zu XText)
- [NetworkX](https://networkx.org/) — Graph-Datenstruktur & Traversierung
- [Claude API](https://docs.anthropic.com/) — KI-gestützte Extraktion & Textverfeinerung
- [FastAPI](https://fastapi.tiangolo.com/) — Web-API
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) — Dokumentation

---

*Entwickelt nach dem AISE-Prinzip: Mensch entscheidet → KI implementiert → Mensch verifiziert.*
