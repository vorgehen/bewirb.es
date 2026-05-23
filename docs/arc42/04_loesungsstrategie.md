# 4. Lösungsstrategie

## Kernentscheidung: Model-Driven Architecture (MDA)

Das System ist selbst ein Beispiel für den Ansatz, den es demonstriert: **Modelle sind erstklassige Artefakte — Code ist abgeleitet, nicht primär.**

```
M2: METAMODELLE
  profile.tx (Profil-Grammatik) + requirements.tx (Anforderungs-Grammatik)
       │
       └── codegen.py generiert → src/models.py, src/graph_schema.py, web/schemas.py

M1: MODELLE
  mein.profile (PIM, plattformunabhängig) + job_xyz.req (Anforderungen)
       │
       └── M2M-Transformation: PIM × Anforderungen → PSM (job_xyz_tailored.profile)

M0: AUSGABEN (M2T-Generatoren)
  word_generator  → .docx + .pdf
  html_generator  → .html
  md_generator    → .md
  highlights_generator → Kurzprofil
  anschreiben_generator → Anschreiben .docx
```

## Vier tragende Prinzipien

| Prinzip | Umsetzung im System |
|---|---|
| **DDD** | Ubiquitous Language in `docs/ubiquitous_language.md` ist bindend in Code, DSL und Dokumentation. TextX-Grammatik *ist* das Domänenmodell. |
| **MDD** | `profile.tx` + `requirements.tx` sind die Quelle der Wahrheit. `codegen.py` leitet Code automatisch ab. Grammatikänderung → einmal `codegen.py` ausführen → alle Klassen aktuell. |
| **TDD** | Jede neue Funktion hat Tests vor "fertig". 6 Testebenen (Grammar, Codegen, DataLoader, M2M, Contract, API). CI läuft bei jedem Push. |
| **AISE** | Claude API im Produkt für Extraktion und Textgenerierung. Claude Code im Prozess für Implementierung. KI-Beiträge in Commits transparent markiert. |

## Hybride KI-Strategie

KI wird gezielt eingesetzt — nicht pauschal für alles:

| Aufgabe | Mechanismus | Begründung |
|---|---|---|
| Anforderungsextraktion | Claude API | Freitext → strukturierte `.req`-Datei — schlecht regelbasiert |
| Projekt-Matching | NetworkX Graph-Traversierung | Deterministisch, nachvollziehbar, kein KI-Overhead |
| Textverfeinerung PSM | Claude API (optional) | Formulierungen auf Ausschreibung zuspitzen |
| Anschreiben | Claude API | Fließtext — KI-Stärke; Mensch verifiziert vor Versand |
| Generatoren (Word/HTML/MD) | Jinja2-Templates | Reine Transformation, kein KI-Bedarf |

## Technologie-Entscheidungen (Kurzform)

| Entscheidung | Wahl | ADR |
|---|---|---|
| Sprache | Python 3.12 | ADR-001 |
| DSL-Framework | TextX | ADR-002 |
| Zwei DSLs statt einer | `profile.tx` + `requirements.tx` getrennt | ADR-003 |
| KI-Einsatz | Hybrid (Graph + Claude) | ADR-004 |
| Web-Framework | FastAPI | ADR-005 |
| Entwicklungsprozess | AISE | ADR-006 |
| Domänenmodell | DDD | ADR-007 |
