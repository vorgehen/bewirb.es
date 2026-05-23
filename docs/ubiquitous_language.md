# Ubiquitous Language — Glossar

Dieses Glossar ist **bindend** in Code, DSL, Tests, Dokumentation und Gespräch.  
Abweichungen sind Bugs, keine Stilfragen.

## Kernbegriffe

| Begriff | Definition | Nicht verwenden |
|---|---|---|
| `Profil` | Die vollständige Menge aller Berufserfahrungen einer Person (PIM — Platform-Independent Model). Entspricht `profile.tx`-Instanz. | CV, Lebenslauf, Resume |
| `Projekterfahrung` | Ein konkretes abgeschlossenes oder laufendes Projekt mit Auftraggeber, Zeitraum, Rolle und eingesetzten Technologien. | Job, Assignment, Einsatz |
| `Ausschreibung` | Ein konkretes Stellenangebot eines Auftraggebers für eine Freiberufler-Rolle. | Job Posting, Stelle, Anzeige |
| `Anforderungen` | Die aus einer Ausschreibung extrahierten strukturierten Kriterien (MustHave, NiceToHave, Rolle, Branche). Entspricht `requirements.tx`-Instanz. | Requirements, Specs, Kriterien |
| `Auftraggeber` | Die Person oder Organisation, die eine Ausschreibung veröffentlicht. | Client, Customer, Kunde |
| `MaßgeschneidertesProfil` | Das PSM (Platform-Specific Model) — gefiltertes und gewichtetes Profil für eine konkrete Ausschreibung. | Angepasster Lebenslauf, tailored CV |
| `Technologiekompetenz` | Eine Technologie mit Proficiency-Level, Jahren Erfahrung und Schlagworten. | Skill, Technology Stack, Fähigkeit |
| `Profillink` | Ein zeitlich begrenzter, individueller Link für einen Auftraggeber zum Abrufen des MaßgeschneidertenProfils. | Share Link, Link, URL |
| `Profil-Inhaber` | Die Person, deren Profil im System verwaltet wird. Nutzer des CLI/Web. | User, Kandidat, Bewerber |

## MDA-Begriffe

| Begriff | Definition |
|---|---|
| `PIM` | Platform-Independent Model — das vollständige Profil (`mein.profile`), plattform- und jobunabhängig |
| `PSM` | Platform-Specific Model — das MaßgeschneidertesProfil für eine konkrete Ausschreibung |
| `M2M` | Model-to-Model-Transformation — PIM × Anforderungen → PSM |
| `M2T` | Model-to-Text-Transformation — PSM → Ausgabedatei (Word, HTML, Markdown) |
| `Metamodell` | Die TextX-Grammatik (`profile.tx`, `requirements.tx`) — definiert, was ein gültiges Modell ist |

## Bounded-Context-Begriffe

| Begriff | Context | Definition |
|---|---|---|
| `ExtractionService` | Extraction | Transformiert Freitext-Ausschreibung → `.req`-Datei |
| `MatchingService` | Matching | Berechnet Relevanz-Score: Profil × Anforderungen |
| `RefinementService` | Matching | Verfeinert PSM-Texte auf Ausschreibung (KI-gestützt) |
| `ProfileRepository` | Profile | Lädt/speichert `.profile`-Dateien (TextX-validiert) |
| `AnforderungenRepository` | Requirements | Lädt/speichert `.req`-Dateien |
| `ProfilinkRepository` | Sharing | CRUD für zeitlich begrenzte Links (SQLite) |
