# 1. Einführung und Ziele

## Aufgabenstellung

Der **Profile Generator** ist ein Python-basiertes Werkzeug für Freiberufler. Es nimmt einen Ausschreibungstext als Eingabe und erzeugt daraus ein maßgeschneidertes Bewerbungsprofil in mehreren Formaten (Word, PDF, HTML, Markdown).

Das System folgt dem Model-Driven Architecture (MDA)-Ansatz: Zwei DSLs (TextX) beschreiben das Domänenmodell formal. Alle generierten Artefakte leiten sich von diesen Modellen ab — Code ist Konsequenz des Modells, nicht umgekehrt.

## Qualitätsziele

| Priorität | Qualitätsziel | Szenario |
|---|---|---|
| 1 | **Erweiterbarkeit** | Ein neues Ausgabeformat (z.B. JSON) kann ohne Änderung der Grammatiken als neuer Generator hinzugefügt werden. |
| 2 | **Korrektheit des Matchings** | Bei einer Ausschreibung für Java-Architektur erscheinen Java-Projekte dominant im generierten Profil (≥90% Übereinstimmung mit manueller Auswahl). |
| 3 | **Portierbarkeit** | Ein anderer Nutzer kann das System mit seinen eigenen Profildaten betreiben, ohne Code zu ändern — nur `data/`-Verzeichnis und `.env` werden ausgetauscht. |
| 4 | **Wartbarkeit** | Eine Grammatikänderung in `profile.tx` propagiert automatisch durch `codegen.py` in alle generierten Klassen — kein manuelles Anpassen von `models.py`. |

## Stakeholder

| Rolle | Erwartung |
|---|---|
| **Nutzer / Profil-Inhaber** | Maßgeschneidertes Profil in <5 Minuten, minimaler manueller Aufwand. Volle Kontrolle über Inhalt. |
| **Ausschreiber** | Erhält per zeitlich begrenztem Link ein Profil als HTML-Seite und PDF-Download. Kein Login nötig. |
| **Entwickler (andere Nutzer des Tools)** | Kann das Tool mit eigenen Daten betreiben. Klare Trennung zwischen Code und Daten. Dokumentation ausreichend für Einstieg. |
| **GitHub-Reviewer / Auftraggeber** | Sieht ein vollständiges, professionelles Softwareprojekt als Kompetenznachweis: ARC42, ADRs, Tests, CI. |
