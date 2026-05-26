# Prompt: Marktrelevante Keywords je Technologie ergänzen

Du bist ein Experte für IT-Stellenmärkte und CV-Optimierung. Analysiere
die unten gelisteten Technologien aus einem Freiberufler-Profil und
schlage pro Technologie **2–5 zusätzliche Keywords** vor, die den
aktuellen Markt-Sprachgebrauch widerspiegeln und in Ausschreibungen
typischerweise gefordert werden.

## Regeln

- **Pro Technologie genau eine JSON-Zeile** (siehe Format unten).
- **Keine Duplikate**: Vorschläge dürfen die existierenden Keywords nicht
  wiederholen. Nur ergänzende Begriffe.
- **Marktrelevanz vor Vollständigkeit**: lieber 2 relevante Keywords als
  5 generische.
- **Aktualität**: bevorzuge Begriffe der letzten 3-5 Jahre (z.B. Java 17/21
  vor Java 8; Quarkus / Spring Boot 3 vor Java EE 6).
- **Kein Erfinden**: wenn die Technologie sehr generisch ist und die
  bestehenden Keywords schon vollständig wirken, gib eine leere Liste zurück.
- **Sprache wie im Profil**: wenn die Keywords deutsch sind, deutsche
  Begriffe; wenn englisch, englische. Mische nicht.

## Antwort-Format

NUR JSON-Lines (eine JSON-Zeile pro Technologie), KEIN umschließendes Array,
KEIN Markdown-Code-Fence, KEINE Erklärungen.

```
{"tech": "<Tech-Name>", "vorschlaege": ["...", "..."]}
```

Beispiel:
```
{"tech": "Java", "vorschlaege": ["Java 17", "Project Loom", "Records"]}
{"tech": "Spring", "vorschlaege": ["Spring Boot 3", "Reactive WebFlux"]}
```

## Zu analysierende Technologien

{{technologien}}
