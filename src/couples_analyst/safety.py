"""The safety gate. Runs before every other module and can halt the run.

See reference/90-safety.md. The gate does not determine that abuse occurred, does not
classify, and produces no risk score. It reports observable markers and, when any are
present, withholds the conflict-pattern analysis whose symmetry assumption they violate.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .indicators import Evidence
from .lexicon import (
    ADVERSARIAL_REQUEST,
    MINOR_ROMANTIC,
    SAFETY,
    SAFETY_IDIOM_EXCLUDE,
    THIRD_PARTY_REPORT,
    compile_group,
    find_spans,
    fold,
    sentence_around,
)
from .normalize import Transcript, Turn

CATEGORY_LABEL = {
    "threat": "Threat",
    "physical_violence": "Physical violence or its aftermath",
    "intimidation": "Intimidation",
    "monitoring": "Monitoring / surveillance",
    "financial_control": "Financial control",
    "isolation": "Isolation from others",
    "sexual_coercion": "Sexual coercion",
    "expressed_fear": "Fear expressed by one partner",
}

# Pronoun cues for marker direction (90-safety.md sec. 2.1). Direction is reported as the
# text states it; the gate does not adjudicate who the aggressor is.
_SECOND_PERSON_ACTOR = compile_group([
    r"\byou (?:hit|slapped|threw|pushed|shoved|grabbed|choked|kicked|punched|dragged|broke|twisted|held|blocked|cornered|stood over|checked|read|went through|took|closed|froze|kept going|smashed|didn'?t stop)\b",
    r"\byou(?:'ll| will|'re| are) (?:hurt|kill|make sure|going to)\b",
    r"\bwhen you (?:put me|threw me|hit)\b",
    r"\bme (?:pegaste|golpeaste|empujaste|agarraste|ahorcaste|patease|arrastraste|tiraste|aventaste|sujetaste|inmovilizaste|rompiste|torciste)\b",
    r"\b(?:revisaste|leiste|bloqueaste|cerraste|congelaste|rompiste|destrozaste) (?:mi|el|la|tu)\b",
    r"\bte voy a\b",  # quoted back at the partner
])
_FIRST_PERSON_ACTOR = compile_group([
    r"\bi(?:'ll| will|'ve| have)? ?(?:hurt|kill|end|destroy|ruin|take the|report|make sure|checked|read|went through|closed|froze|stopped|drove by|called)\b",
    r"\bgive me your\b",
    r"\bshow me the\b",
    r"\bi don'?t want you\b",
    r"\byou(?:'re| are) not (?:seeing|going|getting)\b",
    r"\b(?:te voy a|voy a (?:hacer|matar|asegurarme|denunciar|llevarme)|revise|lei|mire|llame|cerre|congele)\b",
    r"\bdame (?:tu|la)\b",
    r"\bensename\b",
    r"\bno quiero que (?:veas|estes|hables)\b",
    r"\bno vas a (?:ver|salir|trabajar|ir)\b",
])

# Cues that a marker may not be what it looks like (90-safety.md sec. 3.1).
_AMBIGUITY_CUES = compile_group([
    r"\b(?:joking|kidding|a joke|sarcasm|hypothetically|in the movie|on tv|the show|the book|dream(?:ed|t)?)\b",
    r"\b(?:broma|bromeando|en serio no|hipoteticamente|en la pelicula|en la serie|el libro|sone)\b",
    r"\b(?:she|he|they) said\b",
    r"\b(?:dijo|conto) que\b",
    r"\bwould never\b",
    r"\bnunca (?:te )?(?:haria|lo haria)\b",
])


@dataclass
class SafetyMarker:
    category: str
    evidence: list[Evidence]
    direction: str = "unclear"
    ambiguous: bool = False
    competing_reading: str | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "direction": self.direction,
            "evidence": [e.to_json() for e in self.evidence],
            "ambiguous": self.ambiguous,
            "competing_reading": self.competing_reading,
        }


@dataclass
class SafetyResult:
    tripped: bool = False
    halted_analysis: bool = False
    markers: list[SafetyMarker] = field(default_factory=list)
    statement: str | None = None
    minors_halt: bool = False
    third_party_only: list[Evidence] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return {
            "tripped": self.tripped,
            "halted_analysis": self.halted_analysis,
            "markers": [m.to_json() for m in self.markers],
            "statement": self.statement,
        }


def _direction(turn: Turn, quote_folded: str, category: str, dyad: list[str]) -> str:
    """Map pronoun cues onto dyad ids. 'unclear' where the text does not establish it."""
    other = next((s for s in dyad if s != turn.speaker), None)
    if other is None:
        return "unclear"
    speaker_to_other = f"{turn.speaker}_toward_{other}"
    other_to_speaker = f"{other}_toward_{turn.speaker}"
    # Normalize to the schema's A/B vocabulary where the dyad is A/B.
    def norm(d: str) -> str:
        a, b = "A_toward_B", "B_toward_A"
        if d.startswith("A_toward"):
            return a
        if d.startswith("B_toward"):
            return b
        return "unclear"

    if category == "expressed_fear":
        return norm(other_to_speaker)

    second = any(p.search(quote_folded) for p in _SECOND_PERSON_ACTOR)
    first = any(p.search(quote_folded) for p in _FIRST_PERSON_ACTOR)
    if second and not first:
        return norm(other_to_speaker)
    if first and not second:
        return norm(speaker_to_other)
    if first and second:
        return "mutual_as_stated"
    return "unclear"


def screen(tr: Transcript, lang: str) -> SafetyResult:
    """Screen the transcript. Trips on any marker; errs toward tripping (90-safety sec. 3.1)."""
    result = SafetyResult()
    dyad = tr.dyad

    # Minors: unconditional halt, no coding, no excerpting.
    minor_pats = compile_group(MINOR_ROMANTIC.get(lang, []))
    for t in tr.turns:
        if find_spans(fold(t.text), minor_pats):
            result.minors_halt = True
            result.tripped = True
            result.halted_analysis = True
            result.statement = (
                "The transcript indicates a romantic or sexual relationship involving a minor. "
                "This instrument does not analyze, code, or excerpt such material."
            )
            return result

    idiom = compile_group(SAFETY_IDIOM_EXCLUDE.get(lang, []))
    third_party = compile_group(THIRD_PARTY_REPORT.get(lang, []))

    by_category: dict[str, list[Evidence]] = {}
    ambiguous_by_category: dict[str, str | None] = {}

    for t in tr.turns:
        folded = fold(t.text)
        tp_spans = find_spans(folded, third_party)
        for category, groups in SAFETY.items():
            pats = compile_group(groups.get(lang, []))
            spans = find_spans(folded, pats, exclude=idiom)
            for s, e in spans:
                # Reported speech about a third party is recorded, not tripped on,
                # unless the dyad is implicated in the same sentence.
                qs, qe = sentence_around(t.text, s, e)
                if any(ts <= s and e <= te for ts, te in tp_spans) or any(
                    qs <= ts < qe for ts, _ in tp_spans
                ):
                    result.third_party_only.append(
                        Evidence(t.index, t.speaker, t.text[qs:qe].strip(), (qs, qe),
                                 t.attribution_uncertain)
                    )
                    continue
                ev = Evidence(
                    turn=t.index,
                    speaker=t.speaker,
                    quote=t.text[qs:qe].strip(),
                    char_span=(qs, qe),
                    attribution_uncertain=t.attribution_uncertain,
                )
                by_category.setdefault(category, []).append(ev)
                if any(p.search(folded) for p in _AMBIGUITY_CUES):
                    ambiguous_by_category[category] = (
                        "The turn also carries hedging, reported speech, or a "
                        "non-literal frame, so the marker may not describe the couple's "
                        "own conduct. The gate does not resolve this ambiguity silently."
                    )
                ev_dir = _direction(t, folded, category, dyad)
                setattr(ev, "_direction", ev_dir)

    for category, evs in by_category.items():
        dirs = {getattr(e, "_direction", "unclear") for e in evs}
        definite = dirs - {"unclear"}
        if {"A_toward_B", "B_toward_A"} <= definite or "mutual_as_stated" in definite:
            direction = "mutual_as_stated"
        elif len(definite) == 1:
            # One definite reading plus spans that do not establish direction on their own.
            direction = definite.pop()
        else:
            direction = "unclear"
        note = ambiguous_by_category.get(category)
        result.markers.append(
            SafetyMarker(
                category=category,
                evidence=evs,
                direction=direction,
                ambiguous=note is not None,
                competing_reading=note,
            )
        )

    if result.markers:
        result.tripped = True
        result.halted_analysis = True
        result.statement = (
            "Markers of threat, violence, intimidation, or coercive control are present in "
            "this transcript. The conflict frameworks this instrument implements — negative "
            "interaction cycles, the Four Horsemen, mutual contribution — all assume two "
            "partners with roughly symmetric power to influence each other. Where one "
            "partner controls the other through violence, threat, surveillance, economic "
            "control, or isolation, that assumption does not hold, and describing the "
            "exchange as a shared cycle would misdescribe it and distribute responsibility "
            "to the person being harmed. The standard analysis has therefore been withheld "
            "rather than qualified."
        )
    return result


def screen_request(request_text: str, lang: str) -> str | None:
    """Screen the *user's request* for adversarial use (90-safety.md sec. 4).

    Returns a refusal reason, or None.
    """
    if not request_text:
        return None
    pats = compile_group(ADVERSARIAL_REQUEST.get(lang, []))
    if find_spans(fold(request_text), pats):
        return (
            "This request asks the instrument to produce an asymmetric, blame-assigning "
            "output — a case against one partner, evidence for a dispute, a verdict on who "
            "is right, a diagnosis of someone who is not here, or an analysis the other "
            "partner does not know about. The instrument codes dyadic interaction "
            "descriptively and states its findings symmetrically; used as ammunition it "
            "would produce exactly the output it is built not to produce, and its codes are "
            "not evidence of anything in a legal or clinical sense.\n\n"
            "What it can do instead: a symmetric description of the interaction pattern that "
            "both partners could read, with each claim anchored to a quoted turn and what "
            "the analysis cannot establish stated up front."
        )
    return None
