# ADR-002: Model-Driven Architecture als Kernansatz

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

Ein Profil-Generator könnte einfach als direktes Mapping implementiert werden: Profildaten einlesen → Template füllen → Ausgabe. Das wäre schneller zu bauen. Die Alternative ist ein vollständiger MDA-Ansatz mit Metamodellen, DSLs und generierten Klassen.

## Entscheidung

**MDA-Ansatz:** Zwei TextX-DSLs (M2) sind die Quelle der Wahrheit. Alle Code-Artefakte (`models.py`, `graph_schema.py`, `schemas.py`) werden aus dem Metamodell generiert. Die Transformationspipeline folgt strikt M2→M1→M0.

## Begründung

**Dreifacher Zweck des Projekts:**

1. **Praktisches Tool:** MDA ermöglicht, neue Ausgabeformate als neue Generatoren hinzuzufügen, ohne Datenstrukturen anzupassen — das Metamodell bleibt stabil.

2. **Principal-Showcase:** Ein Senior-Architekt, der MDA nicht nur beschreibt, sondern praktisch anwendet, demonstriert Kompetenz überzeugender als Behauptungen.

3. **Selbstdokumentation:** Das System ist selbst ein Beispiel für den Ansatz — "Ich beherrsche MDSD nicht nur theoretisch, ich wende es auf mein eigenes Profil-System an."

**Direktes Mapping hätte diese Nachteile:**
- Grammatikänderung → manuelle Anpassung aller betroffenen Klassen
- Kein formaler Vertrag zwischen Daten und Code
- Kein Showcase-Wert

## Konsequenzen

- **Positiv:** Grammatikänderung → einmal `codegen.py` → alle Klassen aktuell. Neue Generatoren ohne Datenstrukturanpassung. Vollständige ARC42-Dokumentierbarkeit.
- **Negativ:** Höherer initialer Aufwand (Phase 1 + Phase 2 vor erster Funktion).
- **Invariante:** `src/models.py` und `src/graph_schema.py` werden nie manuell bearbeitet.
