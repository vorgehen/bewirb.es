# 5. Bausteinsicht

## C4 Level 2 — Container

```mermaid
C4Container
    title Container — Profile Generator

    Person(nutzer, "Nutzer / Profil-Inhaber")
    Person(ausschreiber, "Ausschreiber")

    System_Boundary(profgen, "Profile Generator") {
        Container(cli, "CLI", "Python", "generate_profile.py —<br>Einstiegspunkt für Profilgenerierung.")
        Container(webapp, "Web App", "FastAPI + HTML/JS", "Profillinks mit Ablaufdatum,<br>Monaco-Editor für .profile/.req.")
        Container(codegen, "Code-Generator", "Python / TextX", "Liest Grammatik (M2) →<br>generiert src/models.py, schemas.py.")
        ContainerDb(files, "Profil-Dateien", "Filesystem", ".profile (PIM), .req (Anforderungen),<br>PSM (tailored.profile).")
        ContainerDb(sqlite, "Link-Store", "SQLite", "Zeitlich begrenzte Profillinks<br>mit UUID und Ablaufdatum.")
    }

    System_Ext(claude, "Claude API", "Anthropic")

    Rel(nutzer, cli, "Startet Generierung", "PowerShell")
    Rel(nutzer, webapp, "Bearbeitet DSL-Dateien", "Browser / Monaco")
    Rel(ausschreiber, webapp, "Öffnet Profillink", "Browser / HTTPS")
    Rel(cli, files, "Liest PIM + .req,<br>schreibt PSM + Output")
    Rel(cli, claude, "Extraktion + Verfeinerung", "HTTPS")
    Rel(webapp, sqlite, "CRUD Profillinks")
    Rel(webapp, files, "Liest PSM für Download")
    Rel(codegen, files, "Liest profile.tx →<br>schreibt models.py")
```

## C4 Level 3 — Component (CLI-Pipeline)

```mermaid
C4Component
    title Component — CLI-Pipeline (src/)

    Container_Boundary(cli, "CLI / Core (src/)") {
        Component(loader, "DataLoader", "data_loader.py", "TextX parse → NetworkX Graph.<br>Liest .profile und .req.")
        Component(processor, "InputProcessor", "input_processor.py", "Freitext → .req-Datei<br>(KI-gestützt via AiRefiner).")
        Component(pim2psm, "PimToPsm", "pim_to_psm.py", "M2M: PIM × Anforderungen → PSM.<br>Graph-Traversierung + KI-Scoring.")
        Component(refiner, "AiRefiner", "ai_refiner.py", "Claude API Wrapper.<br>Prompt-Templates, Caching.")
        Component(word_gen, "WordGenerator", "generators/word_generator.py", "PSM → .docx + .pdf")
        Component(html_gen, "HtmlGenerator", "generators/html_generator.py", "PSM → HTML (Jinja2)")
        Component(md_gen, "MdGenerator", "generators/md_generator.py", "PSM → Markdown")
        Component(high_gen, "HighlightsGenerator", "generators/highlights_generator.py", "PSM+req → Kurzprofil")
        Component(anschr_gen, "AnschreibenGenerator", "generators/anschreiben_generator.py", "PSM+req → Anschreiben (KI)")
    }

    Container_Boundary(web, "Web App (web/)") {
        Component(api, "ProfilinkAPI", "web/app.py", "FastAPI Routen:<br>Link anlegen, öffnen, Download.")
        Component(editor, "Monaco-Editor", "web/editor/", "DSL-Editor im Browser.")
    }

    ContainerDb(files, "Profil-Dateien", "Filesystem")
    ContainerDb(sqlite, "Link-Store", "SQLite")
    System_Ext(claude, "Claude API")

    Rel(pim2psm, loader, "Nutzt")
    Rel(pim2psm, refiner, "KI-Scoring & Textverfeinerung")
    Rel(processor, refiner, "Anforderungsextraktion")
    Rel(loader, files, "Liest .profile / .req")
    Rel(pim2psm, files, "Schreibt PSM")
    Rel(word_gen, pim2psm, "Erhält PSM")
    Rel(html_gen, pim2psm, "Erhält PSM")
    Rel(md_gen, pim2psm, "Erhält PSM")
    Rel(refiner, claude, "API-Aufrufe")
    Rel(api, sqlite, "CRUD Links")
    Rel(api, files, "Liest PSM für Download")
```

## Baustein-Beschreibungen

| Baustein | Datei | Verantwortung |
|---|---|---|
| `DataLoader` | `src/data_loader.py` | TextX-Parser → NetworkX-Graph. Einziger Einstiegspunkt für Modelldaten. |
| `InputProcessor` | `src/input_processor.py` | Freitext-Ausschreibung → valide `.req`-Datei via Claude API. |
| `PimToPsm` | `src/pim_to_psm.py` | M2M-Transformation: Graph-Traversierung + optionales KI-Scoring → PSM. |
| `AiRefiner` | `src/ai_refiner.py` | Zentraler Claude-API-Wrapper. Prompt-Caching, strukturierter Output, Langfuse-Observability. |
| `WordGenerator` | `src/generators/word_generator.py` | PSM → `.docx` (python-docx) + `.pdf` (docx2pdf). |
| `HtmlGenerator` | `src/generators/html_generator.py` | PSM → HTML via Jinja2-Template. |
| `HighlightsGenerator` | `src/generators/highlights_generator.py` | Top-Matches aus PSM-Scoring → einseitiges Kurzprofil. |
| `AnschreibenGenerator` | `src/generators/anschreiben_generator.py` | PSM + Anforderungen → Anschreiben via Claude API. |
| `ProfilinkAPI` | `web/app.py` | FastAPI: Link anlegen, öffnen, Download, Ablauf-Prüfung. |
| `codegen` | `codegen/codegen.py` | Liest `profile.tx` → generiert `src/models.py`, `src/graph_schema.py`, `web/schemas.py`. |

> **Invariante:** `src/models.py` und `src/graph_schema.py` werden ausschließlich von `codegen.py` geschrieben — nie manuell bearbeitet.
