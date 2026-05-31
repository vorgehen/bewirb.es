person Profil_Inhaber {
    title: "Senior Software Ingenieur & Architekt"
    contact {
        email: "profil@beispiel.de"
        location: "Deutschland"
        linkedin: "linkedin.com/in/beispiel"
        github: "github.com/beispiel"
    }
    kurzprofil: "Senior-Architekt mit langjähriger Erfahrung in Enterprise-Java, Microservices und modellgetriebener Softwareentwicklung — von der Anforderungsanalyse bis zur Inbetriebnahme."
    persoenlicheDaten {
        geburtsdatum: "1980-01-01"
        staatsangehoerigkeit: "Deutsch"
        familienstand: "Verheiratet"
    }
}

branche Finanzsektor {
    label: "Finanz- und Versicherungssektor"
}

branche Logistiksektor {
    label: "Logistik und Supply Chain"
}

branche ITSektor {
    label: "Informationstechnologie"
}

auftraggeber Auftraggeber_A {
    label: "Grossbank AG"
    location: "Frankfurt"
}

auftraggeber Auftraggeber_B {
    label: "Logistik GmbH"
    location: "Hamburg"
}

auftraggeber Auftraggeber_C {
    label: "IT-Beratung AG"
    location: "Muenchen"
}

projekt Projekt_A {
    title: "Modernisierung einer Kernbankanwendung"
    auftraggeber: Auftraggeber_A
    branche: Finanzsektor
    periode: 2022-01 to 2024-06
    rolle: "Senior Java Architekt"
    uses: [wg_enterprise_java, wg_microservices]
    keywords: ["Bankwesen", "Modernisierung", "Microservices", "Integration"]
    description: "Migration einer monolithischen Kernbankanwendung auf eine Microservices-Architektur."
    achievements: ["Latenz um 40% reduziert", "Deploymentfrequenz von monatlich auf taeglich erhoeht"]
}

projekt Projekt_B {
    title: "Logistikplattform fuer Supply-Chain-Management"
    auftraggeber: Auftraggeber_B
    branche: Logistiksektor
    periode: 2020-03 to 2021-12
    rolle: "Lead Developer und Architekt"
    uses: [wg_enterprise_java]
    keywords: ["Logistik", "Integration", "API", "B2B"]
    description: "Entwicklung einer zentralen Integrationsplattform fuer die Lieferkette."
}

projekt Projekt_C {
    title: "Architektur-Review und Dokumentation"
    auftraggeber: Auftraggeber_C
    branche: ITSektor
    periode: 2019-06 to 2020-02
    rolle: "Architekt"
    uses: [wg_enterprise_java]
    keywords: ["Architektur", "Dokumentation", "Review"]
    description: "Durchfuehrung eines Architektur-Reviews und Erstellung vollstaendiger ARC42-Dokumentation."
}

ausbildung Studium {
    title: "Informatik (M.Sc.)"
    institution: "Technische Universitaet Beispielstadt"
    periode: 2005-10 to 2010-09
    abschluss: "Master of Science"
}

sprache deutsch {
    bezeichnung: "Deutsch"
    level: Muttersprache
}

sprache englisch {
    bezeichnung: "Englisch"
    level: Verhandlungssicher
}

zertifikat zertifikat_arch {
    titel: "Certified Software Architecture Professional"
    aussteller: "iSAQB"
    jahr: 2018
}

zertifikat zertifikat_scrum {
    titel: "Professional Scrum Master I"
    aussteller: "Scrum.org"
    jahr: 2020
}

werdegang anstellung_a {
    titel: "Senior Software Engineer"
    arbeitgeber: "Beispiel IT-Beratung GmbH"
    periode: 2010-10 to 2015-09
    beschreibung: "Festanstellung mit Schwerpunkt JEE-Architektur und Mentoring."
}

werdegang anstellung_b {
    titel: "Software Engineer"
    arbeitgeber: "Frueherer Arbeitgeber AG"
    periode: 2000-04 to 2010-09
    beschreibung: "Einstieg in die kommerzielle Softwareentwicklung; Schwerpunkt Java/JEE."
}

schluesselkompetenzen {
    methodenkompetenz: ["Modellgetriebene Entwicklung", "TDD", "Domain-Driven Design"]
    fachkompetenz: ["Finanzsektor", "Logistik"]
    fuehrungkompetenz: ["Mentoring", "Stakeholder-Management"]
    programmierparadigmen: ["Objektorientierung", "Funktional", "Deklarativ (DSL)"]
}

wissensgebiet wg_enterprise_java {
    titel: "Enterprise Java"
    reihenfolge: 1
    architekturstil: "N-Tier / Java EE"
    Sprache: ["Java (8–17)"]
    Framework: ["Spring", "Spring Boot"]
    Persistenz: ["JPA / Hibernate"]
    Schnittstellen: ["REST", "OpenAPI"]
    Plattform: ["Linux"]
    Test: ["JUnit", "Mockito"]
}

wissensgebiet wg_microservices {
    titel: "Microservices & Cloud"
    reihenfolge: 2
    architekturstil: "Microservices / Container"
    Plattform: ["Docker", "Kubernetes"]
    Schnittstellen: ["REST", "gRPC"]
    Werkzeug: ["Git", "GitHub Actions"]
}

wissensgebiet wg_python_mdd {
    titel: "Python & MDD"
    reihenfolge: 3
    architekturstil: "Modellgetrieben"
    Sprache: ["Python"]
    Framework: ["FastAPI"]
    Grammatik: ["TextX"]
    Test: ["pytest"]
    Dokumentation: ["ARC42", "C4"]
}
