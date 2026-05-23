# 6. Laufzeitsicht

## Szenario 1: Profilgenerierung (Hauptpfad)

Der Nutzer hat eine Ausschreibung als Freitext und möchte ein maßgeschneidertes Profil erzeugen.

```mermaid
sequenceDiagram
    actor Nutzer
    participant CLI as generate_profile.py
    participant IP as InputProcessor
    participant AI as AiRefiner (Claude API)
    participant DL as DataLoader
    participant P2P as PimToPsm
    participant Gen as Generatoren

    Nutzer->>CLI: --profile mein.profile --text ausschreibung.txt
    CLI->>IP: extract_requirements(ausschreibung.txt)
    IP->>AI: Prompt: Freitext → strukturierte Anforderungen
    AI-->>IP: JSON (Rolle, MustHave, NiceToHave, Keywords)
    IP-->>CLI: job.req (TextX-valide Datei)

    CLI->>DL: load(mein.profile)
    DL-->>CLI: PIM-Graph (NetworkX)
    CLI->>DL: load(job.req)
    DL-->>CLI: Anforderungs-Graph

    CLI->>P2P: transform(PIM-Graph, Anforderungs-Graph)
    P2P->>P2P: Graph-Traversierung + Scoring
    P2P->>AI: Prompt: Texte auf Ausschreibung zuspitzen (optional)
    AI-->>P2P: verfeinerte Beschreibungen
    P2P-->>CLI: PSM-Graph

    CLI->>Gen: generate_all(PSM-Graph)
    Gen-->>Nutzer: job_output.docx + .pdf + .html + highlights.docx + anschreiben.docx
```

## Szenario 2: Ausschreiber öffnet Profillink

```mermaid
sequenceDiagram
    actor Ausschreiber
    participant Web as FastAPI (web/app.py)
    participant DB as SQLite (Link-Store)
    participant FS as Dateisystem (PSM)

    Ausschreiber->>Web: GET /p/{uuid}
    Web->>DB: lookup(uuid)
    DB-->>Web: Link-Eintrag (Ablaufdatum, PSM-Pfad)
    alt Link abgelaufen
        Web-->>Ausschreiber: 410 Gone — "Profil nicht mehr verfügbar"
    else Link gültig
        Web->>DB: increment Zugriffszähler
        Web->>FS: load PSM
        FS-->>Web: PSM-Daten
        Web-->>Ausschreiber: HTML-Profilseite mit PDF-Download
    end
```

## Szenario 3: Code-Generierung (Entwicklerpfad)

```mermaid
sequenceDiagram
    actor Entwickler
    participant CG as codegen.py
    participant TX as TextX (profile.tx)
    participant FS as Dateisystem

    Entwickler->>CG: python codegen/codegen.py
    CG->>TX: parse grammar/profile.tx
    TX-->>CG: Metamodell (Klassen, Attribute, Referenzen)
    CG->>FS: write src/models.py (Pydantic-Klassen)
    CG->>FS: write src/graph_schema.py (NetworkX-Knoten)
    CG->>FS: write web/schemas.py (FastAPI-Schemas)
    CG-->>Entwickler: "3 Dateien generiert"
```
