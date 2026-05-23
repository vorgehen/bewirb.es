# ADR-001: Python als Implementierungssprache

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

Der Profil-Inhaber ist Senior-Software-Architekt mit primärer Expertise in Java/XText. Das Tool wird aber auf einem Windows-Arbeitsrechner betrieben und soll für andere Freiberufler portierbar sein. Die Wahl der Sprache beeinflusst DSL-Framework, KI-Bibliotheken und die Hürde für andere Nutzer.

## Entscheidung

**Python 3.12** als einzige Implementierungssprache für alle Komponenten (Core, CLI, Web, Codegen).

## Begründung

| Kriterium | Python | Java |
|---|---|---|
| KI-Bibliotheken | `anthropic`, `langfuse` — First-Class | Java-SDK vorhanden, aber Community kleiner |
| DSL-Framework | TextX — Python-nativ, XText-ähnliche Syntax | XText — Java/Eclipse, schwerer portierbar |
| Web-Framework | FastAPI — modern, schnell, typsicher | Spring Boot — mehr Infrastruktur nötig |
| Installation | `pip install` — eine Zeile | Maven/Gradle + JVM |
| Portierbarkeit | `requirements.txt` reicht | komplexer Build-Prozess |
| Interop | `docx2pdf` (Windows COM) direkt verfügbar | umständlicher |

TextX ist für Python-Nutzer das direkte Äquivalent zu XText in Java — dieselbe Grammatiksyntax, derselbe Denkansatz, andere Laufzeit.

## Konsequenzen

- **Positiv:** Maximale Portierbarkeit, minimale Einstiegshürde, beste KI-Library-Unterstützung.
- **Negativ:** Der Profil-Inhaber muss Python lernen/vertiefen (kein Problem — bewusstes Upskilling).
- **Risiko:** `docx2pdf` benötigt Microsoft Word auf Windows; auf Linux/Mac ist LibreOffice nötig.
