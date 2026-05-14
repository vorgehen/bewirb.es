# CLAUDE.md — Projektkontext für KI-Assistenten

## Was ist dieses Projekt?
Python-basierter MDA-Profil-Generator für Freiberufler-Bewerbungen.
Input: Ausschreibungstext → Output: maßgeschneidertes Word+PDF+HTML-Profil.
Das Repo selbst ist ein Principal-Level-Architektur-Showcase (ARC42 + ADRs).

## Vier Kernprinzipien
1. **DDD** — Ubiquitous Language (siehe `docs/ubiquitous_language.md`) ist bindend
2. **MDD** — `grammar/profile.tx` + `grammar/requirements.tx` sind die Quelle der Wahrheit
3. **TDD** — Jede neue Funktion hat Tests, bevor sie "fertig" ist
4. **AISE** — KI-Beiträge werden in Commits mit `Co-Authored-By` markiert

## Ubiquitous Language (bindend im gesamten Code)
- `Profil` (nicht: CV, Lebenslauf, Resume)
- `Projekterfahrung` (nicht: Job, Assignment)
- `Ausschreibung` (nicht: Stellenangebot, Job Posting)
- `Anforderungen` (nicht: Requirements, Specs)
- `Auftraggeber` (nicht: Client, Kunde)
- `MaßgeschneidertesProfil` (nicht: angepasster Lebenslauf)
- `Profillink` (nicht: Share Link)

## Wichtige Strukturregeln
- Persönliche `.profile`- und `.req`-Dateien gehören NICHT ins Repo (`.gitignore`)
- `data/example/` enthält nur anonymisierte Demo-Daten
- `src/models.py` und `src/graph_schema.py` sind AUTO-GENERATED von `codegen/codegen.py` — nicht manuell bearbeiten
- Alle Claude-API-Aufrufe laufen über Prompt-Templates in `prompts/*.md`

## Verzeichnisstruktur (Kurzübersicht)
```
grammar/        # TextX-DSL-Grammatiken (profile.tx, requirements.tx)
codegen/        # Code-Generator aus Metamodell → src/models.py
src/            # Core-Module (data_loader, matcher, pim_to_psm, generators/)
scripts/        # CLI-Skripte (extract, update, create_link, build_docs, extract_competencies)
web/            # FastAPI Web-App
prompts/        # Claude-API-Prompt-Templates
docs/           # ARC42 + ADRs + Methodik
data/example/   # Anonymisierte Demo-Daten
tests/          # pytest (unit, integration, snapshot, eval)
```

## Testausführung
```powershell
pytest tests/ -m "not integration and not eval"  # schnell, kein API-Key nötig
pytest tests/ -m integration                      # benötigt ANTHROPIC_API_KEY
```

## Code-Qualität
```powershell
ruff check src/ web/ scripts/ codegen/
mypy src/ web/ codegen/
bandit -r src/ web/
```
