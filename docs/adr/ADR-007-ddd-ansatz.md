# ADR-007: Domain-Driven Design als Strukturprinzip

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

Das System modelliert eine Domäne (Freiberufler-Bewerbungen) mit eigenem Vokabular. Ohne explizites Domänenmodell entstehen typische Probleme: inkonsistente Bezeichner (CV vs. Resume vs. Profil), verwischte Verantwortungsgrenzen, schwer testbare Module.

## Entscheidung

**DDD als strukturierendes Prinzip** — Strategic und Tactical:

**Strategic DDD:**
- Bounded Contexts: Extraction, Profile, Matching, Generation, Sharing, Requirements
- Ubiquitous Language: bindend in Code, DSL, Tests und Dokumentation

**Tactical DDD:**
- Aggregates: `Profile` (Root: Person), `JobApplication` (Root: Anforderungen)
- Entities: `Projekterfahrung`, `Technologiekompetenz`, `MaßgeschneidertesProfil`, `Profillink`
- Value Objects: `Periode`, `Rolle`, `UUID`, `Ablaufdatum`
- Domain Services: `MatchingService`, `ExtractionService`, `RefinementService`
- Repositories: `ProfileRepository`, `AnforderungenRepository`, `ProfilinkRepository`

## Kernaussage

**Die TextX-Grammatik `profile.tx` *ist* das Domänenmodell.** Ubiquitous Language und Metamodell sind dasselbe Artefakt. Das ist die zentrale Synergie zwischen DDD und MDD:

```
Ubiquitous Language → TextX-Grammatik → codegen.py → Pydantic-Klassen → Code
```

Ein Begriffswechsel in der Domäne propagiert von der Grammatik durch alle generierten Artefakte.

## Begründung

Ohne explizite Ubiquitous Language entstehen Inkonsistenzen: "Job" vs. "Projekt", "Client" vs. "Auftraggeber", "Resume" vs. "Profil" — quer durch Code, Tests und Dokumentation. DDD erzwingt Konsistenz strukturell, nicht durch Konvention.

## Konsequenzen

- **Positiv:** Einheitliche Sprache in Code, DSL, Tests, Dokumentation und Gespräch. Klare Modulgrenzen.
- **Bindend:** `CLAUDE.md` listet die verbotenen Synonyme — auch KI-Tools müssen sich daran halten.
- **Glossar:** `docs/ubiquitous_language.md` ist die autoritative Referenz.
