# Prompt: CV/Profil-Dokument → .profile DSL

Du bist ein Experte für die strukturierte Erfassung von Freiberufler-Profilen.
Wandle den folgenden Text aus einem CV/Profildokument in die unten beschriebene
**`.profile` DSL** um.

**Antwort-Format — strikt:**
- NUR gültiger DSL-Text, keine Erklärungen, keine Vorrede.
- KEINE Markdown-Code-Fences (` ``` `).
- KEINE Bullet-Marker (`*`, `-`) vor String-Werten. Alle Listen-Werte
  stehen in `["...", "..."]`-Form ohne führende Sterne.
- KEINE `**bold**`-Markierungen.
- Strings IMMER in doppelten Anführungszeichen. Interne `"` als `\"`.

## DSL-Format (Ubiquitous Language)

Die Reihenfolge der Elemente ist frei. Bezeichner (Identifier nach `person`,
`branche`, …) sind ASCII, ohne Leerzeichen, beginnend mit Buchstabe; nutze
`_` für Wortgrenzen.

### Person (genau eine)

```
person <Id> {
    title: "<Berufsbezeichnung>"
    contact {
        email: "<email>"
        phone: "<phone>"           # optional
        location: "<Stadt/Land>"   # optional
        website: "<url>"           # optional
        linkedin: "<url>"          # optional
        github: "<url>"            # optional
    }
    kurzprofil: "<2–4 Sätze>"     # optional
    persoenlicheDaten {           # optional
        geburtsdatum: "YYYY-MM-DD"
        geburtsort: "..."
        staatsangehoerigkeit: "..."
        familienstand: "..."
        kinder: "..."
    }
}
```

### Branche (mehrere)

```
branche <Id> { label: "<Klartext-Name>" }
```

### Auftraggeber (mehrere)

```
auftraggeber <Id> {
    label: "<Firmenname>"
    location: "<Stadt>"   # optional
}
```

### Technologiekompetenz (mehrere)

```
technology <Id> {
    category: <Programmiersprache | Framework | Datenbank | Cloud | Werkzeug | Methodik | Plattform | Protokoll>
    proficiency: <Experte | Fortgeschritten | Grundkenntnisse>
    years: <ganze Zahl>
    keywords: ["...", "..."]   # optional
}
```

### Projekterfahrung (mehrere)

```
projekt <Id> {
    title: "<Projekttitel>"
    auftraggeber: <Auftraggeber-Id>
    branche: <Branche-Id>
    periode: YYYY-MM to YYYY-MM       # oder ... to today
    rolle: "<Rolle im Projekt>"
    uses: [<TechId>, <TechId>]        # optional, Referenzen
    keywords: ["..."]                  # optional
    description: "<Kurzbeschreibung>"  # optional
    achievements: ["...", "..."]       # optional
}
```

### Werdegang — Festanstellungen (mehrere, optional)

```
werdegang <Id> {
    titel: "<Position>"
    arbeitgeber: "<Firmenname>"
    periode: YYYY-MM to YYYY-MM   # oder ... to today
    beschreibung: "..."            # optional
}
```

### Ausbildung (mehrere)

```
ausbildung <Id> {
    title: "<Bezeichnung>"
    institution: "<Hochschule/Schule>"
    periode: YYYY-MM to YYYY-MM
    abschluss: "<Grad/Abschluss>"  # optional
}
```

### Sprache (mehrere, optional)

```
sprache <Id> {
    bezeichnung: "<Name>"
    level: <Muttersprache | Verhandlungssicher | Gut | Grundkenntnisse>
}
```

### Zertifikat (mehrere, optional)

```
zertifikat <Id> {
    titel: "<Titel>"
    aussteller: "<Organisation>"
    jahr: <ganze Zahl>
    url: "<url>"   # optional
}
```

### Schlüsselkompetenzen (höchstens einmal, optional)

```
schluesselkompetenzen {
    methodenkompetenz: ["..."]   # optional
    fachkompetenz: ["..."]       # optional
    technologie: ["..."]         # optional
    spezialgebiet: ["..."]       # optional
    fuehrungkompetenz: ["..."]   # optional
}
```

## Regeln

- Reichere mit allem an was klar im Dokument steht — erfinde nichts.
- Wenn ein Datum ungenau ist (nur Jahr), nutze `YYYY-01` als Monat.
- Aktuelle Tätigkeit: `to today`.

### Identifier-Konvention

Identifier (das Wort nach `person`/`branche`/`technology`/…) sind ASCII,
beginnen mit Buchstabe, dürfen nur Buchstaben/Ziffern/`_` enthalten.

- **`technology`:** Der Identifier IST der suchbare Name. Idiomatisch ohne
  Präfix und so nah am echten Namen wie möglich:
  - "Java" → `Java`
  - "Spring Boot" → `Spring_Boot`
  - "Java EE" → `Java_EE`
  - "JPA / Hibernate" → `JPA_Hibernate`
  - ".NET Core" → `dotNet_Core`
  - "C#" → `CSharp`
  - "Apache Camel" → `Apache_Camel`
  KEIN `tech_`-Präfix, KEIN Lowercase-Zwang. Bei Mehrwort-Begriffen Underscore
  statt Leerzeichen.
- **`auftraggeber`:** Sprechend, z.B. `Bundesoberbehoerde_Finanzaufsicht`,
  `Telekom_Deutschland`, `IT_Beratung_GmbH`. KEIN nummerierter Index.
- **`branche`:** Kurz und sprechend: `Finanzsektor`, `Telekommunikation`,
  `oeffentliche_Verwaltung`.
- **`projekt`:** Kurzcode aus dem Dokument wenn vorhanden (z.B. `APP`, `BPS`,
  `BAKHUB`), sonst sprechend wie `Modernisierung_Kernbank`.
- **`person`:** Eine eindeutige ID wie `vorname_nachname` oder Initialen.

### Cross-References

`projekt.auftraggeber`, `projekt.branche` und `projekt.uses[]` verweisen auf
die jeweiligen Identifier — Namen müssen exakt übereinstimmen.

### Inhaltliche Heuristiken

- `years` in Technologiekompetenz: konservativ aus Projektzeiträumen ableiten,
  Maximum die längste durchgängige Erfahrung.
- Bei Auftraggebern wo eine Anonymisierung im Dokument bereits geschehen ist,
  übernimm die anonyme Bezeichnung.
- **Sprachen:** Auch wenn im Dokument nur als Wort genannt (z.B. nur "Englisch"),
  als `sprache`-Block aufnehmen. Wenn kein Level angegeben: `Gut` als Default.
  Deutsch als `Muttersprache` ergänzen wenn das Dokument auf Deutsch ist und
  der Name deutsch klingt.
- **Zertifikate:** Alle aufnehmen, auch ältere — der Nutzer entscheidet später
  was relevant ist. Auch akademische Weiterbildungen mit Zertifikat-Charakter
  (z.B. MITx-Kurse, Coursera-Kurse) sind Zertifikate.
- **Schlüsselkompetenzen:** Wenn das Dokument einen Abschnitt "Kompetenzen",
  "Skills", "Spezielles IT-Know-How", "Kernkompetenzen" o.ä. enthält, in den
  fünf Kategorien (methodenkompetenz / fachkompetenz / technologie /
  spezialgebiet / fuehrungkompetenz) sinnvoll aufteilen. Wenn unklar wo etwas
  hingehört, lieber in zwei Kategorien als gar nicht.

## Zu verarbeitender Profil-Text

{{profil_text}}
