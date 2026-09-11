"""Indicator records and the confidence scale declared in reference/00-epistemics.md.

Confidence is computed, not asserted. Every penalty applied is recorded on the indicator so
a reader can audit the number instead of trusting it.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Literal

from .normalize import Turn

InferenceLevel = Literal["observed", "inferred"]
Band = Literal["strong", "tentative", "insufficient"]

# 00-epistemics.md sec. 3
STRONG_FLOOR = 0.80
EVIDENCE_FLOOR = 0.50
INFERRED_CAP = 0.65

# 00-epistemics.md sec. 3.1
BASE_BY_SPAN_COUNT = {0: 0.0, 1: 0.55, 2: 0.72}
BASE_THREE_PLUS = 0.85

PENALTY = {
    "ambiguous": (0.85, "span also satisfies a competing construct"),
    "inferred": (0.80, "inference beyond the text required"),
    "attribution_uncertain": (0.80, "speaker attribution for a span is uncertain"),
    "short_transcript": (0.85, "transcript under 8 turns"),
    "counter_indicator": (0.85, "a same-module counter-indicator is present"),
}


@dataclass
class Evidence:
    turn: int
    speaker: str
    quote: str
    char_span: tuple[int, int] | None = None
    attribution_uncertain: bool = False

    @classmethod
    def from_turn(cls, turn: Turn, quote: str) -> "Evidence":
        start = turn.text.lower().find(quote.lower())
        if start >= 0:
            verbatim = turn.text[start : start + len(quote)]
            span = (start, start + len(quote))
        else:  # quote is the whole turn
            verbatim, span = turn.text, (0, len(turn.text))
        return cls(
            turn=turn.index,
            speaker=turn.speaker,
            quote=verbatim,
            char_span=span,
            attribution_uncertain=turn.attribution_uncertain,
        )

    def to_json(self) -> dict[str, Any]:
        d: dict[str, Any] = {"turn": self.turn, "speaker": self.speaker, "quote": self.quote}
        if self.char_span:
            d["char_span"] = list(self.char_span)
        if self.attribution_uncertain:
            d["attribution_uncertain"] = True
        return d


@dataclass
class Indicator:
    indicator_id: str
    module: str
    construct: str
    theory_source: str
    unit: Literal["dyad", "speaker"]
    rationale: str
    not_licensed: str
    evidence: list[Evidence] = field(default_factory=list)
    counter_evidence: list[Evidence] = field(default_factory=list)
    speaker: str | None = None
    present: bool = True
    inference_level: InferenceLevel = "observed"
    ambiguous: bool = False
    competing_reading: str | None = None
    confidence: float = 0.0
    confidence_band: Band = "insufficient"
    confidence_factors: list[str] = field(default_factory=list)
    # Populated when the indicator falls below the evidentiary floor.
    what_is_missing: str = ""

    def score(self, *, transcript_turns: int, counter_indicator: bool = False) -> "Indicator":
        """Apply reference/00-epistemics.md sec. 3.1. Penalties only; never a bonus."""
        n = len(self.evidence)
        conf = BASE_THREE_PLUS if n >= 3 else BASE_BY_SPAN_COUNT.get(n, 0.0)
        factors: list[str] = [f"{n} qualifying span(s) -> base {conf:.2f}"]

        def apply(key: str) -> None:
            nonlocal conf
            factor, why = PENALTY[key]
            conf *= factor
            factors.append(f"x{factor} ({why})")

        if self.ambiguous:
            apply("ambiguous")
        if self.inference_level == "inferred":
            apply("inferred")
            if conf > INFERRED_CAP:
                conf = INFERRED_CAP
                factors.append(f"capped at {INFERRED_CAP} (inferred)")
        if any(e.attribution_uncertain for e in self.evidence):
            apply("attribution_uncertain")
        if transcript_turns < 8:
            apply("short_transcript")
        if counter_indicator:
            apply("counter_indicator")

        self.confidence = round(conf, 3)
        self.confidence_band = band_for(self.confidence)
        self.confidence_factors = factors
        return self

    @property
    def is_finding(self) -> bool:
        return self.confidence >= EVIDENCE_FLOOR and bool(self.evidence)

    def to_json(self) -> dict[str, Any]:
        d = {
            "indicator_id": self.indicator_id,
            "module": self.module,
            "construct": self.construct,
            "theory_source": self.theory_source,
            "present": self.present,
            "unit": self.unit,
            "speaker": self.speaker if self.unit == "speaker" else None,
            "evidence": [e.to_json() for e in self.evidence],
            "inference_level": self.inference_level,
            "confidence": self.confidence,
            "confidence_band": self.confidence_band,
            "confidence_factors": self.confidence_factors,
            "rationale": self.rationale,
            "not_licensed": self.not_licensed,
        }
        if self.counter_evidence:
            d["counter_evidence"] = [e.to_json() for e in self.counter_evidence]
        if self.confidence_band == "tentative" or self.competing_reading:
            d["competing_reading"] = self.competing_reading or (
                "Sparse or ambiguous evidence: the span admits a reading in which the "
                "construct is not present."
            )
        return d


@dataclass
class RuledOut:
    """A construct actively searched for, not found, where it could have appeared."""

    module: str
    construct: str
    basis: str
    counter_evidence: list[Evidence] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "construct": self.construct,
            "basis": self.basis,
            "counter_evidence": [e.to_json() for e in self.counter_evidence],
        }


@dataclass
class NotAssessable:
    module: str
    construct: str
    reason: str
    measurement_layer: Literal["unmeasured", "no_occasion"] = "no_occasion"

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ModuleResult:
    """What one module emits. Modules never see each other's results (00-epistemics sec. 4)."""

    module: str
    indicators: list[Indicator] = field(default_factory=list)
    ruled_out: list[RuledOut] = field(default_factory=list)
    not_assessable: list[NotAssessable] = field(default_factory=list)
    competing_readings: list[dict[str, Any]] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    # Only the cycle-level module (30-eft) sets this; the composition layer reads it.
    cycle: dict[str, Any] | None = None


def band_for(confidence: float) -> Band:
    if confidence >= STRONG_FLOOR:
        return "strong"
    if confidence >= EVIDENCE_FLOOR:
        return "tentative"
    return "insufficient"
