# ADR-009: Autorenschaft in KI-assistierter Entwicklung

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

Dieses Projekt wurde mit intensiver KI-Unterstützung (Claude) entworfen und wird KI-assistiert implementiert. Das Meta-Programm (Phase 6) kann Kompetenzen aus beliebigen Plänen extrahieren — auch aus diesem Plan selbst. Die Frage entsteht: Wessen Kompetenzen werden dabei sichtbar?

## Beobachtung

Co-kreierte Artefakte haben untrennbare Autorenschaft:
- **KI bringt:** Musterwissen, Konzeptverbindungen, technische Optionen, Formulierungen
- **Mensch bringt:** Domänenerfahrung, Entscheidungshoheit, Richtungskontrolle, Qualitätsurteil
- **Ergebnis:** gehört der Kollaboration — nicht isoliert einem Autor

## Entscheidung

Das Meta-Programm extrahiert Kompetenzen des **Artefakts**, nicht eines Autors. Kompetenzen aus co-kreierten Dokumenten werden explizit als Kollaborationsergebnisse markiert.

Autorenschaft wird in zwei Dimensionen transparent gemacht:

1. **Commits:** `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>` wo KI wesentlich beitrug
2. **COMPETENCIES.md:** Abschnitt "Entstehungskontext" dokumentiert den AISE-Ansatz und den Anteil menschlicher Entscheidungen

## Kernaussage

> *"Nicht wer das Keyboard bedient, sondern wer die richtigen Fragen stellt und die Antworten beurteilt, demonstriert Kompetenz."*

Die Verantwortung für alle Entscheidungen (Architektur, Richtung, Qualität) liegt beim Menschen. KI-Beiträge sind Werkzeug, keine Urheberschaft.

## Konsequenzen

- **Positiv:** Volle Transparenz über KI-Nutzung — kein Verstecken, kein Übertreiben.
- **Showcase:** Dieser ADR selbst ist ein Kompetenznachweis: ein Principal-Architekt, der KI-Nutzung ethisch und methodisch reflektiert.
- **Bindend:** Alle wesentlichen KI-Commits werden mit `Co-Authored-By` markiert.
