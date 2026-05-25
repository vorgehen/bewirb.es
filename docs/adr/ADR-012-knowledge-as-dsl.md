# ADR-012: Knowledge Layer als DSL (statt YAML)

**Status:** Akzeptiert
**Datum:** 2026-05-25
**Phase:** 7.6

## Kontext

Phase 7.5 hatte den Knowledge Layer (Technologie-Taxonomie, Kompetenzgraph,
Rollenprofile, Opinions) als YAML-Dateien angelegt — pragmatisch und schnell
schreibbar. Bei der Reflexion zeigte sich aber:

- Das Projekt ist als MDA-Showcase positioniert. MDD ist die Source of Truth,
  durchgesetzt durch TextX-Grammatiken und Codegen (ADR-002, ADR-003).
- YAML brach diese Konsistenz: ein ganzer Layer war auf Lookup-Tabellen reduziert,
  ohne Cross-Reference-Validierung, ohne typisierte Modelle, ohne Ubiquitous Language.
- Besonders `opinions.yaml` war faktisch eine Regel-DSL, die als Config getarnt wurde.

## Entscheidung

Knowledge Layer wird als **eine** TextX-Grammatik mit mehreren Entitäten realisiert,
analog zu `grammar/profile.tx`.

```
grammar/knowledge.tx           ← EINE Grammatik
   ├── Technology              (Taxonomie-Einträge mit Aliase und SFIA-Kurve)
   ├── TechnologyRelation      (Kompetenzgraph mit typisiertem Relationstyp)
   ├── RoleProfile             (mit CompetencyArea als Sub-Struktur)
   ├── Preference              (Bias: prefer/over)
   ├── WarnRule, BoostRule, DeprioritizeRule  (Bias: Indikator-Listen)
```

Datei-Konvention: `*.knowledge`, thematisch in Dateien aufgeteilt für Lesbarkeit:

```
knowledge/
  ├── taxonomy.knowledge       (Technologien + Relationen)
  ├── opinions.knowledge       (Bias-Regeln)
  └── roles/*.knowledge        (eine Rolle pro Datei)
```

## Begründung

**Eine Grammatik statt vier** (`taxonomy.tx`, `competency.tx`, `role.tx`, `opinion.tx`):

- Folgt der bestehenden Projekt-Konvention: `profile.tx` definiert ebenfalls sechs
  Entitäten (Person, Technologiekompetenz, Branche, Auftraggeber, Projekterfahrung,
  Ausbildung) in einer Grammatik.
- Cross-References werden natürliche Inter-Entitäts-Verweise im selben Metamodell
  (`source: [Technology]`) statt komplexer Inter-Grammatik-Referenzen.
- Eine Codegen-Invokation, ein Metamodell, eine mentale Abstraktion.
- Die Showcase-Wirkung der Opinion-as-DSL steckt im Konzept der expliziten Bias-Sprache,
  nicht in der Datei-Trennung.

**DSL statt YAML:**

- Typisierte Pydantic-Modelle in `src/models.py` durch Codegen
- Cross-Reference-Validierung: `TechnologyRelation.source` muss eine deklarierte
  `Technology` sein — der Parser fängt fehlerhafte Verweise zur Ladezeit
- Ubiquitous Language: jede Entität hat einen sprechenden Namen, jede Relation einen
  typisierten Kind (`benoetigt`, `ueberschneidet_sich_mit`, `erweitert`, `impliziert`)
- Konsistenz zum Rest des Projekts (MDD-Prinzip aus ADR-002)

## Konsequenzen

**Positiv:**
- MDD-Konsistenz wiederhergestellt
- `src/advisor.py` (Phase 8a) kann gegen typisierte Klassen entwickelt werden,
  nicht gegen `dict[str, Any]`
- Schema-Evolution diszipliniert: Stufe-2-Erweiterungen ändern eine Grammatik,
  generierte Modelle werden automatisch aktualisiert
- `opinions.knowledge` ist als eigenständige Bias-DSL ein Showcase-Artefakt

**Negativ:**
- Einmalige Migration aller Stufe-1-Inhalte (durch one-shot Migrations-Skript erledigt)
- Etwas mehr Boilerplate beim Anlegen neuer Einträge (geschweifte Klammern,
  Schlüsselwörter) — als Tradeoff für Typsicherheit akzeptiert

## Verworfene Alternativen

- **YAML beibehalten** — bricht MDD-Konsistenz, kein typisierter Zugriff, keine
  Cross-Reference-Validierung
- **Vier separate Grammaten** (`taxonomy.tx`, `competency.tx`, `role.tx`, `opinion.tx`)
  — überengineered, bricht Projekt-Konvention; Cross-References zwischen Grammatiken
  sind unnötig komplex
- **Migration auf später verschieben** — Phase 8a würde dann auf `dict[str, Any]` aufbauen,
  was später teuer zu refaktorieren wäre

## Verwandte ADRs

- ADR-002 (MDA-Ansatz)
- ADR-003 (zwei DSLs Profil + Anforderungen) — knowledge.tx fügt die dritte hinzu
- ADR-008 (Meta-Programm)
