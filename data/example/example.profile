person Profil_Inhaber {
    title: "Senior Software Ingenieur & Architekt"
    contact {
        email: "profil@beispiel.de"
        location: "Deutschland"
        linkedin: "linkedin.com/in/beispiel"
        github: "github.com/beispiel"
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

technology Java {
    category: Programmiersprache
    proficiency: Experte
    years: 15
    keywords: ["Java", "JEE", "Spring", "JDK"]
}

technology REST {
    category: Protokoll
    proficiency: Experte
    years: 10
    keywords: ["REST", "HTTP", "OpenAPI", "Swagger"]
}

technology Microservices {
    category: Methodik
    proficiency: Fortgeschritten
    years: 7
    keywords: ["Microservices", "Docker", "Kubernetes"]
}

technology ARC42 {
    category: Methodik
    proficiency: Experte
    years: 8
    keywords: ["ARC42", "Architekturdokumentation", "C4"]
}

technology Python {
    category: Programmiersprache
    proficiency: Fortgeschritten
    years: 5
    keywords: ["Python", "FastAPI", "pytest"]
}

projekt Projekt_A {
    title: "Modernisierung einer Kernbankanwendung"
    auftraggeber: Auftraggeber_A
    branche: Finanzsektor
    periode: 2022-01 to 2024-06
    rolle: "Senior Java Architekt"
    uses: [Java, REST, Microservices, ARC42]
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
    uses: [Java, REST]
    keywords: ["Logistik", "Integration", "API", "B2B"]
    description: "Entwicklung einer zentralen Integrationsplattform fuer die Lieferkette."
}

projekt Projekt_C {
    title: "Architektur-Review und Dokumentation"
    auftraggeber: Auftraggeber_C
    branche: ITSektor
    periode: 2019-06 to 2020-02
    rolle: "Architekt"
    uses: [ARC42, REST]
    keywords: ["Architektur", "Dokumentation", "Review"]
    description: "Durchfuehrung eines Architektur-Reviews und Erstellung vollstaendiger ARC42-Dokumentation."
}

ausbildung Studium {
    title: "Informatik (M.Sc.)"
    institution: "Technische Universitaet Beispielstadt"
    periode: 2005-10 to 2010-09
    abschluss: "Master of Science"
}
