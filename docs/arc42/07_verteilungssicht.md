# 7. Verteilungssicht

## Deployment-Optionen

Das System unterstützt zwei Betriebsmodi: lokal (Standard) und Cloud (optional für Web-App).

## Lokaler Betrieb (Standard)

```
Arbeitsrechner (Windows 10/11)
├── Python 3.12 (.venv)
├── profile-generator/ (dieses Repo)
│   ├── grammar/          ← Grammatiken (M2)
│   ├── src/              ← Core-Module
│   ├── generate_profile.py  ← CLI-Einstiegspunkt
│   └── web/app.py        ← FastAPI (lokal, optional)
├── data/ (gitignored)
│   ├── mein.profile      ← PIM (persönlich, nicht im Repo)
│   └── jobs/             ← .req-Dateien
└── output/ (gitignored)
    └── job_a/            ← Generierte Dateien
```

**CLI-Nutzung:** Alle Befehle laufen lokal in PowerShell. Kein Server nötig für die reine Profilgenerierung.

**Web-App lokal:** `uvicorn web.app:app --host 127.0.0.1 --port 8000` — nur für Monaco-Editor und Link-Vorschau. SQLite-Datenbank im Projektverzeichnis.

## Cloud-Betrieb (optional, Phase 7)

```
GitHub Actions (CI/CD)
└── ubuntu-latest
    ├── lint (ruff, mypy, bandit)
    ├── test (pytest, kein API-Key)
    └── docs-check (mkdocs build --strict)

Cloud-Hosting (optional)
└── Docker-Container (web/Dockerfile)
    ├── FastAPI + uvicorn
    ├── SQLite (persistenter Volume)
    └── output/ (PSM-Dateien für Download)
```

## Datentrennung

| Datei/Verzeichnis | Ort | Im Repo |
|---|---|---|
| `grammar/*.tx` | Repo | ja — Metamodell ist öffentlich |
| `src/`, `web/`, `codegen/` | Repo | ja — Code ist öffentlich |
| `data/example/` | Repo | ja — nur anonymisierte Demo-Daten |
| `data/mein.profile` | lokal | **nein** — `.gitignore` |
| `data/jobs/*.req` | lokal | **nein** — `.gitignore` |
| `output/` | lokal | **nein** — `.gitignore` |
| `.env` (API-Key) | lokal | **nein** — `.gitignore` |

> **Sicherheitsprinzip:** Das Repo ist jederzeit öffentlich publishbar, weil persönliche und vertrauliche Daten strukturell durch `.gitignore` ausgeschlossen sind.
