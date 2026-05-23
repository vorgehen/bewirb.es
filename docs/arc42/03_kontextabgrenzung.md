# 3. Kontextabgrenzung

## Fachlicher Kontext

Der Profile Generator steht zwischen dem Profil-Inhaber (Nutzer) und dem Ausschreiber. Der Nutzer pflegt sein Profil als DSL-Datei und startet die Generierung. Der Ausschreiber erhält einen zeitlich begrenzten Link und lädt das Profil herunter — ohne direkten Zugang zum System.

## C4 Level 1 — System Context

```mermaid
C4Context
    title System Context — Profile Generator

    Person(nutzer, "Nutzer / Profil-Inhaber", "Freiberufler. Pflegt sein Profil,<br>startet Profilgenerierung via CLI oder Web.")
    Person(ausschreiber, "Ausschreiber", "Öffnet zeitlich begrenzten Profillink,<br>lädt PDF herunter.")

    System(profgen, "Profile Generator", "Generiert maßgeschneiderte Bewerbungsprofile<br>aus DSL-Modellen via MDA-Pipeline.")

    System_Ext(claude, "Claude API (Anthropic)", "KI-gestützte Anforderungsextraktion<br>und Textverfeinerung.")
    System_Ext(github, "GitHub", "Code-Hosting, CI/CD (GitHub Actions),<br>Dokumentations-Hosting (GitHub Pages).")

    Rel(nutzer, profgen, "Nutzt", "CLI / Browser")
    Rel(ausschreiber, profgen, "Öffnet Profillink", "HTTPS")
    Rel(profgen, claude, "API-Aufrufe", "HTTPS / REST")
    Rel(profgen, github, "Push → CI/CD + Docs", "Git / HTTPS")
```

## Externe Schnittstellen

| System | Richtung | Protokoll | Zweck |
|---|---|---|---|
| **Claude API** | ausgehend | HTTPS/REST | Anforderungsextraktion aus Freitext, PSM-Textverfeinerung, Anschreiben-Generierung |
| **GitHub** | ausgehend | Git/HTTPS | Code-Versionierung, CI/CD (GitHub Actions), optionales Docs-Hosting |
| **Dateisystem** | bidirektional | lokale I/O | Lesen von `.profile`/`.req`, Schreiben von Ausgabedateien (Word, PDF, HTML) |
| **Microsoft Word** (COM) | ausgehend | Windows COM | PDF-Export via `docx2pdf` |
