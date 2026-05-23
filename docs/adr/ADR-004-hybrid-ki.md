# ADR-004: Hybride KI-Strategie (Graph + Claude)

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

Für das Matching zwischen Profil und Ausschreibung gibt es zwei Extreme: vollständig regelbasiert (Graph-Traversierung) oder vollständig KI-gestützt (Claude entscheidet alles). Beide haben Nachteile.

## Entscheidung

**Hybridansatz:** Graph-Traversierung für das Matching, Claude API nur für Formulierungen und Extraktion.

| Aufgabe | Mechanismus |
|---|---|
| Anforderungen aus Freitext extrahieren | Claude API |
| Projekte nach Relevanz ranken | NetworkX Graph-Scoring |
| PSM-Texte auf Ausschreibung zuspitzen | Claude API (optional) |
| Anschreiben verfassen | Claude API |
| Word/HTML/MD generieren | Jinja2-Templates (kein KI) |

## Begründung

**Probleme mit "KI für alles":**
- Nicht deterministisch — gleiche Eingabe kann verschiedene Projektauswahl liefern
- Schwer testbar — kein klares Verhalten für Unit-Tests
- Teuer — jede Generierung kostet API-Tokens für das gesamte Profil
- "Black Box" — Nutzer kann nicht nachvollziehen, warum Projekte ausgewählt wurden

**Vorteile des Graph-Scorings:**
- Deterministisch und nachvollziehbar (Scoring-Faktoren: Keyword-Overlap, Aktualität, Branche)
- Testbar — `test_pim_to_psm.py` kann exakte Assertions machen
- Schnell und kostenlos
- Erklärbar: "Java-Projekt X hat Score 0.87 wegen 4/5 Keyword-Matches und aktueller Periode"

**KI dort einsetzen, wo sie stark ist:**
- Freitext → Struktur (Extraktion): KI-Stärke, schlecht regelbasiert
- Formulierungen und Fließtext: KI-Stärke, kein deterministischer Ersatz

## Konsequenzen

- **Positiv:** Deterministisches, testbares Kern-Matching. KI-Kosten nur für Aufgaben ohne Alternative.
- **Negativ:** Zwei verschiedene Mechanismen zu pflegen.
- **Qualitätssicherung:** Contract-Tests mocken die Claude API — Matching-Tests brauchen keinen API-Key.
