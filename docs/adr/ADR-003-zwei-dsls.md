# ADR-003: Zwei getrennte DSLs statt einer

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

Das System verarbeitet zwei grundlegend verschiedene Informationstypen: das persönliche Profil des Freiberuflers (stabil, langlebig) und die Anforderungen einer konkreten Ausschreibung (kurzlebig, jobspezifisch). Diese könnten in einer einzigen DSL zusammengefasst werden oder in zwei getrennten.

## Entscheidung

**Zwei getrennte DSLs:**
- `grammar/profile.tx` — Profil-Grammatik (M2, PIM)
- `grammar/requirements.tx` — Anforderungs-Grammatik (M2)

## Begründung

**Unterschiedliche Lebenszyklen:**

| Aspekt | `profile.tx` | `requirements.tx` |
|---|---|---|
| Änderungsfrequenz | selten (neue Projekte, Technologien) | häufig (jede Ausschreibung anders) |
| Autor | Profil-Inhaber | KI (aus Freitext) oder Nutzer |
| Gültigkeitsdauer | dauerhaft | bis Bewerbungsfrist |
| Datenschutz | persönlich, sensibel | jobspezifisch |

**DDD-Argument:** Profil und Anforderungen sind verschiedene Bounded Contexts mit verschiedenen Aggregates. Sie in einer Grammatik zu vereinen würde diese Trennung verwischen.

**MDA-Argument:** Zwei M2-Modelle ermöglichen die M2M-Transformation (PIM × Requirements → PSM) als expliziten Schritt. Bei einer DSL wäre diese Transformation implizit und schwerer nachvollziehbar.

**Praktischer Vorteil:** Die KI kann `.req`-Dateien aus Freitext generieren — ein stabiles, leicht validierbares Format. Das wäre schwieriger mit einer kombinierten DSL.

## Konsequenzen

- **Positiv:** Klare Trennung, unabhängige Evolution beider Grammatiken, explizite M2M-Transformation.
- **Negativ:** Zwei Grammatiken zu pflegen statt einer.
- **Akzeptiert:** Der Mehraufwand ist minimal; der Gewinn an konzeptueller Klarheit ist erheblich.
