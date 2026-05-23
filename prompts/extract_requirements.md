# Prompt: Anforderungen aus Ausschreibungstext extrahieren

Du bist ein Experte für Freiberufler-Bewerbungen im IT-Bereich.
Analysiere den folgenden Ausschreibungstext und extrahiere die Anforderungen
im angegebenen JSON-Format.

## Regeln

- `rolle`: Die gesuchte Stellenbezeichnung (präzise, wie in der Ausschreibung)
- `branchen`: Branche(n) des Unternehmens oder Projekts (z.B. "Finanzsektor", "E-Commerce")
- `must_have`: Technologien/Fähigkeiten die explizit gefordert werden oder klar zwingend sind
- `nice_to_have`: Technologien/Fähigkeiten die als "von Vorteil" oder "wünschenswert" beschrieben werden
- `keywords`: Weitere relevante Schlagwörter (Methoden, Zertifikate, Soft Skills)
- `context`: Ein Satz zur fachlichen Einordnung des Projekts/der Stelle

Antworte NUR mit dem JSON-Objekt, ohne Erklärungen oder Markdown-Formatierung.

## Ausschreibungstext

{{ausschreibung}}

## Erwartetes JSON-Format

{
  "rolle": "...",
  "branchen": ["..."],
  "must_have": ["...", "..."],
  "nice_to_have": ["...", "..."],
  "keywords": ["...", "..."],
  "context": "..."
}
