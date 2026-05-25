# Prompt: CV/Profil-Dokument → .profile DSL

Du bist ein Experte für die strukturierte Erfassung von Freiberufler-Profilen.
Wandle den folgenden Text aus einem CV/Profildokument in die unten beschriebene
**`.profile` DSL** um. Antworte NUR mit gültigem DSL-Text, **ohne** Erklärungen,
**ohne** Markdown-Code-Fences, **ohne** Kommentare oder Vorrede.

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
- Identifier-Konvention: `auftraggeber_<index>`, `proj_<index>`, `tech_<name_klein>`.
  Lieber sprechend als nummeriert wenn möglich (z.B. `bafin_aufsicht`).
- `years` in Technologiekompetenz: konservativ aus Projektzeiträumen ableiten,
  Maximum die längste Projekt-Erfahrung.
- Bei Auftraggebern wo eine Anonymisierung im Dokument bereits geschehen ist,
  übernimm die anonyme Bezeichnung.

## Zu verarbeitender Profil-Text

{{profil_text}}
