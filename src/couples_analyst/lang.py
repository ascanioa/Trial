"""Language detection for report output. Supports English and Spanish."""

from __future__ import annotations

import re

from .lexicon import fold

_MARKERS = {
    "es": {
        "que", "no", "de", "la", "el", "y", "en", "es", "por", "para", "con", "me", "te",
        "se", "lo", "los", "las", "un", "una", "pero", "como", "mas", "si", "ya", "esta",
        "estoy", "eres", "soy", "yo", "tu", "porque", "cuando", "siempre", "nunca", "hacer",
        "todo", "nada", "muy", "bien", "vos", "usted", "ni", "ese", "eso", "esto", "del",
    },
    "en": {
        "the", "you", "i", "to", "and", "a", "of", "that", "it", "is", "was", "for", "on",
        "with", "but", "not", "are", "this", "have", "just", "do", "don't", "dont", "me",
        "my", "your", "we", "he", "she", "they", "what", "when", "why", "always", "never",
        "about", "like", "know", "think", "because", "so", "all", "get",
    },
}

# Characters that only appear in Spanish text here.
_ES_CHARS = re.compile(r"[ñáéíóúü¿¡]")
_WORD = re.compile(r"[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ']+")


def detect(text: str) -> tuple[str, float]:
    """Return ``(lang, confidence)``. Defaults to English on a tie or on empty input."""
    words = [fold(w) for w in _WORD.findall(text)]
    if not words:
        return "en", 0.0

    scores = {lang: sum(1 for w in words if w in marks) for lang, marks in _MARKERS.items()}
    scores["es"] += 2 * len(_ES_CHARS.findall(text))

    total = sum(scores.values())
    if total == 0:
        return "en", 0.0
    lang = max(scores, key=lambda k: scores[k])
    return lang, round(scores[lang] / total, 3)
