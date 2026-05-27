# Kochbuch — bewirb.es

Operativer Spickzettel: **„Ich will X erreichen — welche Befehle tippe ich?"**

Drei Szenarien (Setup · Pflegen · Bewerben) plus Skript- und Test-Anhang.
Alle Befehle in PowerShell-Syntax (Backtick `` ` `` für Zeilenumbruch).

---

## 0. Konventionen

| Aspekt | Wert |
|---|---|
| Shell | **PowerShell** (Windows; Bash via WSL möglich, dann `\` statt `` ` ``) |
| Virtuelle Umgebung | `.\.venv\Scripts\Activate.ps1` |
| API-Key | `ANTHROPIC_API_KEY` in `.env` (siehe `.env.example`) |
| Pfade | `data/<name>/<name>.profile` (gitignored); Beispiele in `data/example/` |
| Dry-Run | `enrich_profile.py` ohne `--apply` zeigt nur Vorschau, schreibt nicht |

Vor jedem Befehl: venv aktivieren.

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 1. Szenario „Setup" (einmalig)

Erstinstallation bis zur ersten lauffähigen Pipeline.

### 1.1 venv und Abhängigkeiten

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

### 1.2 API-Key konfigurieren

```powershell
Copy-Item .env.example .env
# .env editieren: ANTHROPIC_API_KEY=sk-ant-...
```

### 1.3 Codegen ausführen

Erzeugt `src/models.py`, `src/graph_schema.py`, `web/schemas.py` aus den
TextX-Grammatiken `grammar/profile.tx` und `grammar/requirements.tx`.

```powershell
python codegen/codegen.py
```

> Bei jeder Grammatik-Änderung erneut laufen lassen.

### 1.4 Word-Vorlage erzeugen

```powershell
python scripts/create_template.py
```

Erstellt `templates/profil.docx` (Standard-Pfad für `generate.py --format word`).

### 1.5 Smoke-Test mit Demo-Daten

Ohne API-Key — nutzt das anonymisierte Beispielprofil.

```powershell
python scripts/generate.py data/example/example.profile data/example/example_job.req `
    --format word -o profil_test.docx
```

### 1.6 Test-Suite

```powershell
pytest tests/ -m "not integration and not eval"
```

Integration-Tests (langsam, benötigen `ANTHROPIC_API_KEY`):

```powershell
pytest tests/ -m integration
```

---

## 2. Szenario „Pflegen" (kontinuierlich)

Datenbasis ausbauen und anreichern — die Schritte sind unabhängig.

### 2.1 CV-Dokumente importieren (einmaliger Bootstrap)

Liest `.docx`-Dateien rekursiv, ruft Claude API, schreibt eine `.profile`.

```powershell
python scripts/import_profile.py arbeitsdokumente/profil/ -o data/<name>/<name>.profile
```

Auch Einzeldateien oder Liste möglich:

```powershell
python scripts/import_profile.py cv_2024.docx cv_2025.docx -o draft.profile
```

### 2.2 Kurzprofil neu generieren (Zielgruppen-spezifisch)

```powershell
# Dry-Run (zeigt nur Vorschlag)
python scripts/enrich_profile.py data/<name>/<name>.profile --mode kurzprofil --zielgruppe Consultant

# Tatsächlich in die .profile-Datei schreiben
python scripts/enrich_profile.py data/<name>/<name>.profile --mode kurzprofil --zielgruppe Consultant --apply
```

Verfügbare Zielgruppen:
`Behoerde` · `Consultant` · `StartUp` · `Wissenschaftlich` · `Standard` · `AIGovernance`.

### 2.3 Technologie-Keywords vorschlagen lassen

Claude analysiert alle `technology`-Blöcke und schlägt aktuelle, marktrelevante
Keywords pro Eintrag vor.

```powershell
python scripts/enrich_profile.py data/<name>/<name>.profile --mode keywords           # Dry-Run
python scripts/enrich_profile.py data/<name>/<name>.profile --mode keywords --apply
```

### 2.4 Projektbeschreibung aus Arbeitsartefakten anreichern (NDA-sicher)

Zwei Schritte: erst **anonymisieren**, dann **anreichern**. Der `--preprocess`-Modus
ist Pflicht — er verhindert, dass Kundendokumente direkt an die API gehen.

```powershell
# Schritt 1: Lokale Anonymisierung eines Kunden-Verzeichnisses
python scripts/anonymize_doc.py arbeitsdokumente/<kunde-x>/ `
    -o arbeitsdokumente/_extrakte/<kunde-x>.txt

# Schritt 2 (Dry-Run): Anreicherung mit anonymisiertem Extrakt
python scripts/enrich_profile.py data/<name>/<name>.profile `
    --mode projekt --projekt-id <ProjektID> `
    --preprocess arbeitsdokumente/_extrakte/<kunde-x>.txt

# Schritt 2 (Schreiben)
python scripts/enrich_profile.py data/<name>/<name>.profile `
    --mode projekt --projekt-id <ProjektID> `
    --preprocess arbeitsdokumente/_extrakte/<kunde-x>.txt --apply
```

> `<ProjektID>` ist der `name` des `projekt`-Blocks in der `.profile` —
> der Befehl listet bei Fehler alle verfügbaren IDs auf.

### 2.5 Anonymisierung als eigenständiges Werkzeug

```powershell
# stdout
python scripts/anonymize_doc.py arbeitsdokumente/<kunde-x>/dokument.docx

# In Datei
python scripts/anonymize_doc.py arbeitsdokumente/<kunde-x>/ -o extrakt.txt

# Nur Audit-Log (was würde ersetzt — ohne Text-Output)
python scripts/anonymize_doc.py arbeitsdokumente/<kunde-x>/ --audit-only

# Eigene Konfig statt `anonymize_config.yaml` im Root
python scripts/anonymize_doc.py input.docx --config my_config.yaml
```

Konfig-Schema: `replace:` (Wörterbuch), `public_domain:` (nicht ersetzen),
`patterns:` (eigene Regex). Vorlage: `anonymize_config.yaml` im Repo-Root.

---

## 3. Szenario „Bewerben pro Angebot"

End-to-End: Ausschreibungs-Text → maßgeschneidertes Word-Profil.

### 3.1 Optional vorab: Portfolio-Scan

Welche der vorhandenen Angebote lohnt sich überhaupt?

```powershell
python scripts/advise.py data/<name>/<name>.profile --scan angebote/
```

Ausgabe: Ranking aller `.req`-Dateien nach Match-Score plus wiederkehrende Lücken.

### 3.2 Ausschreibungstext speichern

Text der Stellenanzeige (Stepstone, LinkedIn, ...) als `angebote/<name>.txt` ablegen.

### 3.3 Anforderungen extrahieren

```powershell
python scripts/extract.py angebote/<name>.txt -n <name>
```

Schreibt `angebote/<name>.req`. Claude extrahiert `rolle`, `must_have`,
`nice_to_have`, `keywords`, `context`.

### 3.4 Bewerbung beurteilen (Advisory, Einzel-Modus)

```powershell
python scripts/advise.py data/<name>/<name>.profile angebote/<name>.req
```

Ausgabe: Score-Aufschlüsselung, getroffene `must_have`, unterkommunizierte
Stärken, Lücken nach Schließbarkeit (Artikulation / Zertifizierung /
Erfahrung / strukturell), Pluspunkte, Warnungen.

JSON für Weiterverarbeitung:

```powershell
python scripts/advise.py data/<name>/<name>.profile angebote/<name>.req --json
```

### 3.5 Maßgeschneidertes Word-Profil generieren

```powershell
python scripts/generate.py data/<name>/<name>.profile angebote/<name>.req `
    --format word -o data/<name>/profil_<name>_<angebot>.docx
```

Markdown statt Word (Vorschau):

```powershell
python scripts/generate.py data/<name>/<name>.profile angebote/<name>.req --format markdown
```

Generic ohne `.req` (Standardprofil):

```powershell
python scripts/generate.py data/<name>/<name>.profile --format word -o data/<name>/profil_standard.docx
```

---

## Anhang A — Skript-Referenz

| Skript | Zweck | API-Key nötig? |
|---|---|---|
| `scripts/extract.py` | Ausschreibungstext → `.req` | ja |
| `scripts/import_profile.py` | CV-Dokumente → `.profile` | ja |
| `scripts/enrich_profile.py` | Kurzprofil / Keywords / Projekt anreichern | ja |
| `scripts/anonymize_doc.py` | Lokal-Anonymisierung Level 1 (regelbasiert) | nein |
| `scripts/advise.py` | Bewerbungs-Empfehlung + Portfolio-Scan | nein |
| `scripts/generate.py` | `.profile` + `.req` → Markdown / Word | nein |
| `scripts/create_template.py` | Word-Vorlage erzeugen | nein |
| `scripts/build_plan_docx.py` | Plan-Markdown → Word (pandoc) | nein |
| `codegen/codegen.py` | Grammatik → Pydantic-Modelle | nein |

---

## Anhang B — Test- & Qualitäts-Befehle

```powershell
pytest tests/ -m "not integration and not eval"   # schnell, kein Key
pytest tests/ -m integration                       # benötigt Key
ruff check src/ web/ scripts/ codegen/
mypy src/ web/ codegen/
bandit -r src/ web/
```

Beim Commit laufen `ruff`, `ruff-format`, `mypy`, `bandit` als pre-commit-Hooks.
