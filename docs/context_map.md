# Context Map — Bounded Contexts

## Übersicht

```
┌─────────────────┐     ┌──────────────────┐
│ Extraction      │────▶│ Profile          │
│ Context         │     │ Context          │
│                 │     │ (Upstream)       │
│ Docs → .profile │     │ PIM verwalten    │
└─────────────────┘     └────────┬─────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │      Matching Context     │
                    │  PIM × Requirements → PSM │
                    └────────────┬─────────────┘
                                 │
               ┌─────────────────┼──────────────────┐
               ▼                 ▼                  ▼
    ┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │ Generation      │ │  Sharing     │ │  Requirements    │
    │ Context         │ │  Context     │ │  Context         │
    │ PSM → Word/     │ │  Profillinks │ │  Freitext →      │
    │ HTML/Markdown   │ │  + Ablauf    │ │  .req-Datei      │
    └─────────────────┘ └──────────────┘ └──────────────────┘
```

## Kontext-Beschreibungen

### Extraction Context
**Verantwortung:** Initiale Erstellung eines `.profile` aus bestehenden Dokumenten (Word, PDF, alte Lebensläufe).  
**Schlüssel-Service:** `ExtractionService` (`scripts/extract.py`)  
**Downstream:** Profile Context (liefert PIM)

### Profile Context (Upstream)
**Verantwortung:** Verwaltung und Pflege des PIM. Einzige Quelle der Wahrheit für Profildaten.  
**Schlüssel-Repository:** `ProfileRepository`  
**Invariante:** PIM ist immer TextX-valide gegen `profile.tx`

### Requirements Context
**Verantwortung:** Extraktion strukturierter Anforderungen aus Freitext-Ausschreibungen.  
**Schlüssel-Service:** `ExtractionService` (`src/input_processor.py`)  
**Output:** TextX-valide `.req`-Datei (Instanz von `requirements.tx`)

### Matching Context
**Verantwortung:** M2M-Transformation — PIM × Anforderungen → PSM.  
**Schlüssel-Service:** `MatchingService` (`src/pim_to_psm.py`)  
**Mechanismus:** Graph-Traversierung + optionale KI-Verfeinerung

### Generation Context
**Verantwortung:** M2T-Transformation — PSM → Ausgabedateien.  
**Schlüssel-Komponenten:** `WordGenerator`, `HtmlGenerator`, `MdGenerator`, `HighlightsGenerator`, `AnschreibenGenerator`  
**Input:** Immer PSM (nie direkt PIM)

### Sharing Context
**Verantwortung:** Zeitlich begrenzte Profillinks für Ausschreiber.  
**Schlüssel-Repository:** `ProfilinkRepository` (SQLite)  
**Invariante:** Abgelaufene Links liefern 410 Gone, nie das Profil

## Context-Beziehungen

| Von | Nach | Typ | Beschreibung |
|---|---|---|---|
| Extraction | Profile | Conformist | Extraction liefert, Profile Context ist Upstream |
| Profile | Matching | Customer/Supplier | Matching ist Downstream-Kunde des Profile Context |
| Requirements | Matching | Customer/Supplier | Matching konsumiert Anforderungen |
| Matching | Generation | Customer/Supplier | Generation erhält PSM von Matching |
| Matching | Sharing | Customer/Supplier | Sharing erhält PSM-Pfad von Matching |
