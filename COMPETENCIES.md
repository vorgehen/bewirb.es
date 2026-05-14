# Kernkompetenzen — Abstraktion

> Dieses Dokument destilliert die Prinzipien hinter dem Profile-Generator-Projekt
> auf eine universell anwendbare Ebene. Es ist selbst ein Beispiel der Kompetenz,
> die es beschreibt: Abstraktion.

---

## Abstraktion als Fundament

Die Fähigkeit, aus konkreten Lösungen universelle Prinzipien zu destillieren
und diese Prinzipien bewusst auf neue Problemstellungen anzuwenden.

Ein Principal-Architekt erkennt Muster über Projekte hinweg — und kann artikulieren,
*warum* eine Lösung funktioniert, nicht nur *dass* sie funktioniert.

---

## Dimension 1: Technische Architektur

### DDD — Domain-Driven Design

**Prinzip:** Das Domänenmodell ist die einzige Quelle der Wahrheit.

**Schlüsseleinsicht:** Ubiquitous Language überbrückt Business und Technologie.
Wenn Fachbereich und Entwicklung dieselben Begriffe verwenden, fallen Übersetzungsfehler weg.

**Abstraktes Muster:** Bounded Contexts → klare Verantwortungsgrenzen → lose Kopplung.

**In diesem Projekt:** Die `profile.tx`-Grammatik *erzwingt* die Ubiquitous Language formal —
Domänenmodell und Metamodell sind dasselbe Artefakt.

---

### MDD — Model-Driven Development

**Prinzip:** Modelle sind erstklassige Artefakte — Code ist abgeleitet, nicht primär.

**Schlüsseleinsicht:** Wer das Metamodell kontrolliert, kontrolliert alle Instanzen.
Eine Änderung an der Grammatik propagiert automatisch durch das gesamte System.

**Abstraktes Muster:** M3→M2→M1→M0 + M2M (Modell-zu-Modell) + M2T (Modell-zu-Text).

**In diesem Projekt:** `profile.tx` (M2) generiert via `codegen.py` die Implementierung;
`risch.profile` (M1 PIM) × `job.req` → `tailored.profile` (M1 PSM) → Word/HTML/Markdown.

---

### TDD — Test-Driven Development

**Prinzip:** Tests sind ausführbare Spezifikationen, keine nachgelagerte Qualitätssicherung.

**Schlüsseleinsicht:** Wer zuerst den Test schreibt, denkt zuerst über das Interface nach —
nicht über die Implementierung.

**Abstraktes Muster:** Red→Green→Refactor + kontinuierliche Verifikation (CI).

**In diesem Projekt:** Tests parallel zur Implementierung; generierter Code durchläuft
dieselbe Qualitätskette wie handgeschriebener Code.

---

### AISE — AI-Supported Software Engineering

**Prinzip:** KI verstärkt menschliche Fähigkeiten — ersetzt nicht menschliches Urteil.

**Schlüsseleinsicht:** KI ist am wirksamsten an Grenzen (Entwürfe, Reviews, Generierung),
wo menschliche Intention klar ist und KI-Ausgabe verifizierbar bleibt.

**Abstraktes Muster:** Mensch entscheidet → KI implementiert → Mensch verifiziert.

**In diesem Projekt:** Claude API für Extraktion und Textverfeinerung; KI-Beiträge
in Commits transparent markiert; das System verarbeitet selbst KI-Ausgaben.

---

## Dimension 2: Projektmanagement

### Scope Management

**Prinzip:** Scope wird bewusst und schrittweise erweitert — nie unkontrolliert.

**Schlüsseleinsicht:** Jede Erweiterung wird gegen Prinzipien geprüft, nicht gegen Wünsche.

### Phasierung & Abhängigkeiten

**Prinzip:** Komplexität wird durch sequenzierte Phasen mit expliziten Voraussetzungen beherrschbar.

**Schlüsseleinsicht:** Design-First ist kein Overhead — es ist Risikominimierung.

**Abstraktes Muster:** 0 (Skeleton) → 1 (Design) → 2–N (Implement) → optional (Extend).

### Priorisierung

**Prinzip:** Pflicht und Optional werden explizit getrennt — kein implizites "nice to have".

### Stakeholder-Management

**Prinzip:** Verschiedene Stakeholder haben verschiedene Perspektiven — beide sind gültig.

**In diesem Projekt:** Robert (CLI, Profil pflegen) ≠ Ausschreiber (Link öffnen, PDF laden).

### Qualitätstore

**Prinzip:** Qualität wird durch Gates erzwungen, nicht durch Appelle.

**Abstraktes Muster:** CI/CD + statische Analyse + Tests = nicht-verhandelbare Gates.

### Transparenz über Entscheidungen

**Prinzip:** Das Warum ist wichtiger als das Was — Entscheidungen ohne Begründung sind Schulden.

**Abstraktes Muster:** ADRs als verbindliche Entscheidungsdokumentation.

---

## Dimension 3: Prozess & Agiles Vorgehen

### Iterative & Inkrementelle Entwicklung

**Prinzip:** Wert wird in kleinen, verifizierbaren Schritten geliefert — kein Big Bang.

**Abstraktes Muster:** Roadmap als priorisierter Backlog — Pflicht vor Optional.

### Design-First als Sprint 0

**Prinzip:** Architektur ist kein Overhead — sie ist die erste Investition.

**Abstraktes Muster:** ARC42 + ADRs vor erstem Code (Architecture Runway).

### Definition of Ready & Definition of Done

**Prinzip:** "Bereit" und "Fertig" ohne Kriterien sind keine Aussagen.

**Abstraktes Muster:** DoR = Eintrittskriterien, DoD = Abnahmekriterien — je Phase explizit.

### Kontinuierliche Integration

**Prinzip:** Integration ist kein Ereignis — sie ist ein dauerhafter Zustand.

### XP-Praktiken

TDD, Continuous Integration, einfaches Design (YAGNI), Refactoring als Daueraufgabe.

---

## Dimension 4: Synergien

```
DDD × MDD:      Ubiquitous Language = DSL-Grammatik.
                Domänenmodell und Metamodell sind dasselbe Artefakt.

MDD × TDD:      Generierter Code durchläuft dieselbe Qualitätskette
                wie handgeschriebener. Das System testet, was es selbst generiert.

TDD × AISE:     KI generiert Testentwürfe — Tests verifizieren KI-Ausgaben.
                Zirkuläre Stärke: KI und Tests kontrollieren sich gegenseitig.

DDD × AISE:     Ubiquitous Language im CLAUDE.md → KI versteht die Domäne.
                KI-Ausgaben können am Domänenmodell gemessen werden.

PM × Prozess:   Phasierung + DoR/DoD + ADRs = Governance ohne Bürokratie.

Prozess × alle: Design-First + CI/CD + iterative Verfeinerung rahmen alle
                technischen Prinzipien ein — ohne Prozess bleiben Prinzipien Theorie.
```

---

## Entstehungskontext

Dieses Dokument wurde durch KI-assistierte Planung (AISE) erarbeitet.
Die Entscheidungshoheit lag durchgehend beim Architekten.

> *"Nicht wer das Keyboard bedient, sondern wer die richtigen Fragen stellt
> und die Antworten beurteilt, demonstriert Kompetenz."*

Die extrahierten Kompetenzen sind Ergebnis der Kollaboration — die Verantwortung
für jede Entscheidung ist menschlich.
