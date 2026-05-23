# 2. Randbedingungen

## Technische Randbedingungen

| Randbedingung | Begründung |
|---|---|
| **Python 3.12** | Modernes Python mit vollständigem Typsystem (PEP 695), breite Bibliotheksunterstützung für alle benötigten Komponenten. |
| **Windows-kompatibel** | Primäre Arbeitsumgebung des Profil-Inhabers ist Windows. PDF-Export über `docx2pdf` nutzt Microsoft Word COM. |
| **Kein Datenbankserver** | Keine Infrastruktur-Abhängigkeit. SQLite für Share-Links, Dateisystem für Profile. Läuft ohne Serverinstallation. |
| **Claude API (Anthropic)** | KI-gestützte Extraktion und Textverfassung. API-Key wird lokal in `.env` gespeichert, nie ins Repo committed. |
| **TextX als DSL-Framework** | Python-natives Äquivalent zu Xtext. EBNF-ähnliche Grammatiksyntax, direkte Python-Objektinstantiierung. |
| **NetworkX für Graph** | Bewährte Python-Bibliothek für Graphen. Kein externer Graph-Datenbankserver nötig. |

## Organisatorische Randbedingungen

| Randbedingung | Begründung |
|---|---|
| **Persönliche Daten nicht im Repo** | `.profile`-Dateien, Ausschreibungen und generierte Profile enthalten persönliche und vertrauliche Informationen. `.gitignore` schützt diese Dateien strukturell. |
| **`data/example/` nur anonymisiert** | Demo-Daten im Repo sind vollständig anonymisiert und fiktiv — kein Rückschluss auf reale Personen oder Auftraggeber möglich. |
| **KI-Beiträge transparent** | Commits mit KI-Unterstützung werden mit `Co-Authored-By: Claude Sonnet` markiert. AISE-Ansatz ist dokumentiert, nicht versteckt. |
| **Design-First** | ARC42-Dokumentation und ADRs sind Voraussetzung für jede Implementierung (DoR Phase 2). |

## Konventionen

| Konvention | Geltungsbereich |
|---|---|
| **Ubiquitous Language** | Alle Bezeichner in Code, DSL, Tests und Dokumentation verwenden die in `docs/ubiquitous_language.md` definierten Begriffe. |
| **AUTO-GENERATED** | `src/models.py` und `src/graph_schema.py` werden nie manuell bearbeitet — sie sind Ausgabe von `codegen/codegen.py`. |
| **Prompt-Templates** | Alle Claude-API-Aufrufe verwenden Jinja2-Templates in `prompts/` — keine Inline-Strings im Code. |
