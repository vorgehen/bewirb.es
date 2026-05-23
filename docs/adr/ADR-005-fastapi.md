# ADR-005: FastAPI als Web-Framework

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

Die Web-App (Phase 7) braucht ein Python-Web-Framework für: zeitlich begrenzte Profillinks (CRUD), Profil-HTML-Ansicht, PDF-Download und optionalen Monaco-Editor. Alternativen: Flask, Django, FastAPI.

## Entscheidung

**FastAPI** als Web-Framework.

## Begründung

| Kriterium | FastAPI | Flask | Django |
|---|---|---|---|
| Typsicherheit | Pydantic-nativ, mypy-freundlich | keine | begrenzt |
| Automatische OpenAPI-Docs | ja (Swagger UI) | nein | nein |
| Async-Support | nativ (ASGI) | eingeschränkt | eingeschränkt |
| Lernkurve | gering | sehr gering | hoch |
| Overhead | minimal | minimal | hoch (ORM, Admin, ...) |
| Passt zu Pydantic-Modellen | perfekt | manuell | manuell |

**Entscheidend:** Die generierten `web/schemas.py` sind Pydantic-Klassen — FastAPI versteht diese nativ, ohne Konvertierung. Das ist direkte Konsequenz des MDA-Ansatzes: `profile.tx` → `codegen.py` → `web/schemas.py` → FastAPI nutzt diese direkt.

Django wäre Overengineering für einen einfachen Datei-Download-Service ohne komplexes ORM.

## Konsequenzen

- **Positiv:** Automatische API-Dokumentation, native Pydantic-Integration, modernes async-fähiges Framework.
- **Negativ:** Für statische HTML-Auslieferung etwas mehr Konfiguration als bei Flask.
- **Deployment:** `uvicorn web.app:app` — ein Befehl, kein komplexes Setup.
