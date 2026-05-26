# Prompt: Projekt-Beschreibung aus anonymisiertem Artefakt-Extrakt anreichern

Du bist ein Experte für Freiberufler-Profile. Verbessere die unten gegebene
Projekt-Beschreibung anhand des **bereits anonymisierten** Extrakts aus
Projekt-Artefakten (Architekturpapiere, Konzepte, Reviews).

## Wichtige Vorgaben

- **Der Extrakt ist NDA-bereinigt** — Auftraggebernamen sind durch Platzhalter
  ersetzt ([Finanzaufsichtsbehörde], [Zentralbank], [Bank] etc.). Übernimm
  diese Platzhalter unverändert; **erfinde keine Auftraggebernamen**.
- **Keine vertraulichen Details** in description/achievements: keine internen
  Tickets, Server-Hostnamen, IPs, URLs, Personennamen, BAK-Nummern.
- **Erfinde nichts**, was nicht durch den Extrakt belegt ist. Wenn der Extrakt
  zu wenig hergibt, lieber kürzere Vorschläge.
- **Sprache**: Deutsch, dritte Person Singular oder unpersönlich
  ("verantwortete", "konzipierte", "lieferte").
- **Achievements quantifizieren** wo der Extrakt Zahlen hergibt (z.B. "12 Web
  Services", "Migration von Version 11 auf Version 12"). Sonst lieber konkrete
  Verben ("Ablösung des Mule Service Bus durch JMS").
- **Methoden/Technologien als Substantive**, keine Marketing-Adjektive.

## Antwort-Format

NUR ein JSON-Objekt — keine Code-Fences, keine Erklärungen. Format:

```
{
  "description": "<verbesserte Kurzbeschreibung, 1-3 Sätze>",
  "achievements": ["<konkretes Achievement>", "<noch eines>", ...]
}
```

Wenn description oder achievements nicht verbessert werden sollten, lasse
das jeweilige Feld leer ("" bzw. []).

## Aktueller Projekt-Eintrag

**ID:** {{projekt_id}}
**Titel:** {{projekt_title}}
**Zeitraum:** {{projekt_start}} bis {{projekt_end}}
**Rolle:** {{projekt_rolle}}
**Technologien:** {{projekt_tech}}

**Bisherige description:**
{{projekt_description}}

**Bisherige achievements:**
{{projekt_achievements}}

## Anonymisierter Artefakt-Extrakt

{{extrakt}}
