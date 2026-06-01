"""Tests für src/matcher.py — _term_variants und _matches."""

from src.matcher import _matches, _term_variants

CORPUS = [
    "java (8–17)",
    "spring (core, batch, boot)",
    "n-tier · soa · portal · microservices",
    "python",
    "docker",
    "xtext",
]


class TestTermVariants:
    def test_single_term_unchanged(self) -> None:
        assert _term_variants("Java") == ["java"]

    def test_oder_split(self) -> None:
        result = _term_variants("Java oder TypeScript")
        assert result == ["java oder typescript", "java", "typescript"]

    def test_slash_split(self) -> None:
        result = _term_variants("React/Angular/Vue")
        assert result == ["react/angular/vue", "react", "angular", "vue"]

    def test_oder_and_slash_combined(self) -> None:
        result = _term_variants("Spring Boot oder React/Vue")
        assert "spring boot" in result
        assert "react" in result
        assert "vue" in result


class TestMatches:
    def test_direct_substring(self) -> None:
        assert _matches("python", CORPUS)

    def test_direct_not_in_corpus(self) -> None:
        assert not _matches("rust", CORPUS)

    def test_reverse_substring_catches_hyphen(self) -> None:
        # "microservices" ist Corpus-Item-Substring, "microservices-architektur" die Anforderung
        assert _matches("Microservices-Architektur", CORPUS)

    def test_reverse_substring_catches_version_suffix(self) -> None:
        # Corpus hat "java (8–17)" — Anforderung "java" muss matchen
        assert _matches("java", CORPUS)

    def test_oder_compound_first_alternative_matches(self) -> None:
        assert _matches("Java oder TypeScript", CORPUS)

    def test_oder_compound_second_alternative_matches(self) -> None:
        assert _matches("Rust oder Python", CORPUS)

    def test_slash_compound_matches(self) -> None:
        assert _matches("Docker/Kubernetes", CORPUS)

    def test_no_match_on_unrelated(self) -> None:
        assert not _matches("GenAI/LLM", CORPUS)

    def test_case_insensitive(self) -> None:
        assert _matches("PYTHON", CORPUS)
        assert _matches("Java (8–17)", CORPUS)
