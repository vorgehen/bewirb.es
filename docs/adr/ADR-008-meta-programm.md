# ADR-008: Meta-Programm als Umkehrfunktion des Profil-Generators

**Status:** Akzeptiert (optional, Phase 6)  
**Datum:** 2026-05

## Kontext

Der Profil-Generator transformiert strukturierte Profildaten → maßgeschneiderte Ausgaben (M1→M0). Die umgekehrte Frage: Kann das System aus beliebigen Arbeitsartefakten (Pläne, ADRs, ARC42) abstrakte Kompetenzen destillieren?

## Entscheidung

**`scripts/extract_competencies.py`** als eigenständiges Meta-Programm: Pläne/Dokumente → abstrahierte Kernkompetenzen im Format von `COMPETENCIES.md`.

```
Profil-Generator:   Ausschreibung → relevante Projekterfahrungen  (M1-Ebene)
Meta-Programm:      Plan/Architektur → abstrakte Kompetenzen      (M2-Ebene)
```

Beide Transformationen teilen dieselbe Infrastruktur (Claude API, Prompt-Templates, strukturierter Output).

## Begründung

**Der eigentliche Wert:** Arbeitsdokumente sind keine Kompetenzbehauptungen — sie sind Beweise. Das Meta-Programm destilliert die darin enthaltenen Prinzipien:

> *"Jemand, der so dokumentiert, denkt so."*

**Generalisierbarkeit:** Das System demonstriert, dass es nicht nur für Profil-Generierung taugt — dieselbe MDA-Pipeline ist auf andere Transformationsaufgaben anwendbar. Das erhöht den Showcase-Wert.

**Praktischer Nutzen:** Der Nutzer kann seine eigenen Projekterfahrungen (Architekturdokumente, retrospektive Berichte) als Input übergeben und erhält abstrahierte Kompetenzen — unabhängig vom Profil-Generator.

## Konsequenzen

- **Positiv:** Demonstration von Generalisierbarkeit. Praktisch nutzbar für Kompetenz-Selbstreflexion.
- **Optional:** Phase 6 — erst nach stabilem Core (Phase 4). Kein Blocker für Kernfunktionalität.
- **Neue Dateien:** `scripts/extract_competencies.py`, `prompts/extract_competencies.md`, `COMPETENCIES.md`.
