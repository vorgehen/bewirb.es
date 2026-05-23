# ADR-006: AISE — AI-Supported Software Engineering als Entwicklungsprinzip

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

Dieses Projekt wird mit intensiver KI-Unterstützung (Claude Code) entwickelt. Die Frage ist: Wie wird KI in den Entwicklungsprozess integriert? Vollständige Delegation? Nur für triviale Aufgaben? Oder ein strukturierter Ansatz mit klarer Rollenteilung?

## Entscheidung

**AISE-Prinzip:** Mensch entscheidet → KI implementiert → Mensch verifiziert.

| Verantwortung | Mensch | KI |
|---|---|---|
| Architekturentscheidungen (ADRs) | ja | nein |
| Implementierung (Module, Tests) | Review | Erstentwurf |
| Dokumentation (ARC42) | Freigabe | Erstentwurf |
| Qualitätskontrolle (CI, Tests) | Konfiguration | Ausführung |
| Prompt-Engineering | ja | nein |

## Transparenz

KI-Beiträge sind in Commits sichtbar:
```
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

`docs/methodology.md` dokumentiert den AISE-Ansatz vollständig — welche Teile KI-generiert sind, welche human-refined.

## Begründung

**Warum nicht "KI macht alles":** Architekturentscheidungen ohne menschliches Urteil führen zu generischem Code ohne Domänenwissen. Die Verantwortung für Qualität und Richtung bleibt beim Entwickler.

**Warum nicht "KI nur für Triviales":** KI ist bei komplexen Aufgaben (Erstentwurf Dokumentation, Testgenerierung, Boilerplate) am wertvollsten. Diese zu delegieren spart erheblich Zeit.

**Showcase-Dimension:** Dieser Ansatz demonstriert, wie ein Principal-Architekt KI produktiv führt — nicht als Codeautomat, sondern als verstärktes Werkzeug unter menschlicher Kontrolle.

## Konsequenzen

- **Positiv:** Schnellere Entwicklung ohne Qualitätsverlust. Transparenz über KI-Nutzung als Kompetenznachweis.
- **Negativ:** Konsequente Verifikation aller KI-Outputs erfordert Disziplin.
- **Qualitätsgate:** KI-generierter Code durchläuft dieselbe Pipeline (ruff, mypy, bandit, pytest) wie handgeschriebener.
