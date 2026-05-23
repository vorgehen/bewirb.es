# Methodik — AISE, DDD, MDD, TDD

## Überblick

Dieses Projekt demonstriert vier ineinandergreifende Prinzipien als gelebte Praxis — nicht als Theorie:

```
                ┌─────────────────────────┐
                │           DDD           │
                │   Domain-Driven Design  │
                │   (das FUNDAMENT)       │
                └────────────┬────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
  │     MDD       │  │     TDD       │  │     AISE      │
  │ Das WAS       │  │ Die QUALITÄT  │  │ Das WIE       │
  │ DSL → Graph   │  │ Tests + CI    │  │ KI im Prozess │
  └───────────────┘  └───────────────┘  └───────────────┘
```

## DDD — Domain-Driven Design

**Rolle:** Fundament. Definiert die Sprache und Struktur für alle anderen Prinzipien.

**Umsetzung:**
- `docs/ubiquitous_language.md` — bindender Begriffsrahmen
- `grammar/profile.tx` — Ubiquitous Language formalisiert als Metamodell
- Bounded Contexts in `docs/context_map.md` — klare Verantwortungsgrenzen
- Tactical Patterns: Aggregates, Entities, Value Objects, Domain Services, Repositories

**Schlüsselerkenntnis:** Die TextX-Grammatik *ist* das Domänenmodell. Domänenänderung → Grammatikänderung → `codegen.py` → alle Klassen aktuell.

## MDD — Model-Driven Development

**Rolle:** Formalisierung des Domänenmodells als ausführbares Artefakt.

**Umsetzung:**
- `grammar/profile.tx` + `grammar/requirements.tx` → M2-Metamodelle
- `codegen/codegen.py` → generiert `src/models.py`, `src/graph_schema.py`, `web/schemas.py`
- `src/pim_to_psm.py` → M2M-Transformation (PIM × Anforderungen → PSM)
- `src/generators/` → M2T-Transformationen (PSM → Word/HTML/MD/...)

**Schlüsselerkenntnis:** Code ist Konsequenz des Modells, nicht umgekehrt. Grammatikänderung propagiert automatisch.

## TDD — Test-Driven Development

**Rolle:** Qualitätssicherung. Jede Funktion hat Tests vor "fertig".

**Umsetzung:**
- 6 Testebenen: Grammar → Codegen → DataLoader → M2M → Contract → API
- Pytest-Marker: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.snapshot`
- Contract-Tests: Claude API gemockt — Matching-Tests brauchen keinen API-Key
- CI: `pytest tests/ -m "not integration"` läuft bei jedem Push (GitHub Actions)
- Statische Analyse: ruff, mypy, bandit via pre-commit + CI

**Schlüsselerkenntnis:** Deterministische Matching-Logik (Graph) ist vollständig testbar. KI-Aufrufe werden durch Contract-Tests mit Mocks abgesichert.

## AISE — AI-Supported Software Engineering

**Rolle:** Prozess. KI als verstärkendes Werkzeug unter menschlicher Kontrolle.

**Im Produkt (Claude API):**
- `src/input_processor.py` — Freitext → strukturierte Anforderungen
- `src/ai_refiner.py` — PSM-Texte auf Ausschreibung zuspitzen
- `src/generators/anschreiben_generator.py` — Anschreiben verfassen

**Im Prozess (Claude Code):**
- Planung: iterativer Dialog → dieser Plan entstand in ~20 Iterationen
- Implementierung: KI schreibt Erstentwürfe, Entwickler reviewt und verfeinert
- Dokumentation: KI erstellt ARC42/ADR-Entwürfe, Entwickler gibt frei
- Tests: KI generiert Testfälle aus Grammatikregeln, Entwickler ergänzt Edge Cases

**Transparenz:**
```
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```
Commits mit wesentlichem KI-Anteil werden so markiert.

**Schlüsselerkenntnis:** KI ist am wirksamsten wo Intention klar und Ausgabe verifizierbar. Architekturentscheidungen (ADRs) bleiben menschlich — Code-Umsetzung wird KI-assistiert.

## Synergien

| Kombination | Synergie |
|---|---|
| DDD × MDD | Ubiquitous Language = DSL-Grammatik. Domänenmodell = Metamodell. |
| MDD × TDD | Generierter Code durchläuft dieselbe Qualitätskette wie handgeschriebener. |
| TDD × AISE | KI generiert Testentwürfe — Tests verifizieren KI-Ausgaben. |
| DDD × AISE | Ubiquitous Language in `CLAUDE.md` → KI versteht die Domäne. |
