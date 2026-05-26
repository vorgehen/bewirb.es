# Prompt: Kurzprofil aus .profile-Inhalten generieren

Du bist ein Experte für Freiberufler-Profil-Texte. Generiere ein
**prägnantes Kurzprofil** (3–5 Sätze, max 500 Zeichen) aus den unten
gegebenen Profil-Inhalten.

## Tonalität nach Zielgruppe

Die `zielgruppe`-Variable bestimmt Akzentuierung und Wortwahl:

- **Behoerde** — formal, vollständig, regulatorisch sensibilisiert.
  Hebe Compliance- und Architektur-Tiefe hervor.
- **Consultant** — ergebnisorientiert, Methoden-stark.
  Hebe Stakeholder-Interaktion und Liefer-Verantwortung hervor.
- **StartUp** — dynamisch, breit aufgestellt.
  Hebe Technologiebreite und Eigeninitiative hervor.
- **Wissenschaftlich** — methodisch, präzise.
  Hebe Modellbildung und Forschungs-Tugenden hervor.
- **AIGovernance** — regulatorisch-technisch.
  Hebe AI-Governance, EU AI Act, DORA hervor.
- **Standard** (oder leer) — ausgewogen.
  Senior-Erfahrung, Methoden, Technologie-Schwerpunkte.

## Regeln

- **Schreibe in der dritten Person Singular** (z.B. "verfügt über",
  "verbindet"). Das ist Profil-Konvention für CV-Texte.
- Nutze nur Informationen aus den unten gegebenen Profil-Inhalten —
  erfinde nichts.
- Maximal 5 Sätze, maximal 500 Zeichen.
- Keine Aufzählungs-Listen, keine Markdown-Formatierung.
- Keine Buzzwords ohne konkrete Begründung. Lieber konkret als bunt.
- **Keine namentlichen Auftraggeber im Kurzprofil**. Selbst wenn der
  Profil-Inhalt Auftraggeber namentlich nennt (BaFin, Telekom Deutschland,
  Vivento, ExperTeam etc.), ersetze sie im Kurzprofil-Text durch
  beschreibende Sektor-Begriffe:
  - BaFin / Bundesanstalt für Finanzdienstleistungsaufsicht →
    "Bundesoberbehörde im Finanzaufsichtsbereich" oder "Finanzaufsicht"
  - Telekom Deutschland → "DAX-Telekommunikationskonzern" oder "Telco"
  - Vivento → "Personaldienstleister im Telekommunikationssektor"
  - Bundesbank / BBk → "Zentralbank"
  - Andere konkret benannte Firmen → "Mittelständler"/"Konzern"/"Behörde" je nach Kontext
  Diese Regel gilt auch wenn Auftraggeber-Felder im Profil
  ("Bundesoberbehörde im Finanzaufsichtsbereich") bereits anonymisiert sind —
  übernimm dann die anonyme Form unverändert.
- Keine Anrede an die Leser ("Sie suchen…"), kein Marketingsprech.

**Antwort-Format:** NUR der Kurzprofil-Text, ohne Anführungszeichen,
ohne Erklärungen, ohne Code-Fences, ohne Headlines.

## Profil-Inhalte

**Person:** {{person_title}}

**Zielgruppe (Tonalität):** {{zielgruppe}}

**Bisheriges Kurzprofil (falls vorhanden, als Ausgangspunkt):**
{{kurzprofil_alt}}

**Top-Technologien (nach Erfahrung):**
{{top_technologien}}

**Projekte (Auswahl der letzten Jahre):**
{{projekte}}

**Schlüsselkompetenzen (Methoden):**
{{methoden}}

**Schlüsselkompetenzen (Fachgebiete):**
{{fachgebiete}}

**Werdegang (zusammengefasst):**
{{werdegang}}
