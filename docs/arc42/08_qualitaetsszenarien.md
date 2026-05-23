# 8. Qualitätsszenarien

## Qualitätsbaum

```
Qualität
├── Korrektheit
│   └── Matching-Genauigkeit
├── Effizienz
│   └── Generierungszeit
├── Wartbarkeit
│   ├── Grammatik-Erweiterbarkeit
│   └── Multi-User-Fähigkeit
└── Sicherheit
    └── Datentrennung
```

## Szenarien

### Q1 — Matching-Genauigkeit (Korrektheit)

| | |
|---|---|
| **Quelle** | Nutzer startet Profilgenerierung mit Ausschreibung für Java-Architektur |
| **System** | PimToPsm führt Graph-Traversierung durch |
| **Stimulus** | Ausschreibung enthält: Java, Microservices, REST, Architektur |
| **Antwort** | Java-Projekte und Architektur-Projekterfahrungen erscheinen in den Top-3 des PSM |
| **Messung** | ≥90% Übereinstimmung mit manuell ausgewählten Projekten in Testfällen |

### Q2 — Generierungszeit (Effizienz)

| | |
|---|---|
| **Quelle** | Nutzer mit bestehendem `.profile` (≤20 Projekte) |
| **Stimulus** | `generate_profile.py --profile mein.profile --req job.req` |
| **Antwort** | Alle Ausgabedateien (Word, PDF, HTML, Highlights) erzeugt |
| **Messung** | Gesamtlaufzeit <5 Minuten inkl. Claude API-Aufrufe |

### Q3 — Grammatik-Erweiterbarkeit (Wartbarkeit)

| | |
|---|---|
| **Stimulus** | Entwickler fügt neues Attribut `availability` zur `Person`-Entität in `profile.tx` hinzu |
| **Antwort** | `python codegen/codegen.py` ausführen → `src/models.py`, `src/graph_schema.py`, `web/schemas.py` enthalten das neue Attribut |
| **Messung** | Kein manuelles Editieren der generierten Dateien nötig. `mypy` bleibt grün. |

### Q4 — Multi-User-Fähigkeit (Portierbarkeit)

| | |
|---|---|
| **Stimulus** | Zweiter Nutzer klont das Repo, legt eigene `data/mein.profile` und `.env` an |
| **Antwort** | `generate_profile.py` läuft mit seinen Daten ohne Code-Änderung |
| **Messung** | Smoke Test grün, Profilgenerierung erfolgreich — kein Fork, kein Branch nötig |

### Q5 — Datentrennung (Sicherheit)

| | |
|---|---|
| **Stimulus** | Entwickler führt `git add .` und `git push` aus |
| **Antwort** | Persönliche `.profile`-Dateien, `.req`-Dateien, `output/`-Verzeichnis und `.env` werden nicht committed |
| **Messung** | `git status` zeigt diese Dateien als "ignored" — kein manuelles Ausschließen nötig |
