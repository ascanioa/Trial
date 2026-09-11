"""Composition layer.

Runs the safety gate first, then hands each module the normalized transcript and nothing
else. Modules are called with no shared mutable state and cannot read one another's output
(reference/00-epistemics.md sec. 4); composition happens only after all coding is done.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from . import SCHEMA_VERSION, __version__, lang as lang_mod
from .indicators import EVIDENCE_FLOOR, Indicator, ModuleResult
from .normalize import Transcript, normalize
from .safety import SafetyResult, screen, screen_request
from .modules import attachment, behavioral, bowen, eft, gottman, interdependence

# Order is presentation order only. It has no effect on coding.
MODULES: list[tuple[str, Callable[[Transcript, str], ModuleResult]]] = [
    ("10-attachment", attachment.code),
    ("20-gottman-levenson", gottman.code),
    ("30-eft", eft.code),
    ("40-bowen-systems", bowen.code),
    ("50-interdependence", interdependence.code),
    ("60-behavioral", behavioral.code),
]

STANDING_LIMITATIONS = [
    "This is a descriptive coding of one text transcript. It is not a diagnosis, not a "
    "clinical assessment, and not a prediction of any outcome.",
    "Text only: no tone of voice, volume, pacing, facial expression, gesture, or touch. "
    "Sarcasm, warmth and contempt are carried substantially by those channels.",
    "No physiological data. Arousal and flooding — central to the Levenson side of this "
    "research — are unmeasured here, not absent.",
    "One conversation, one moment. Nothing here describes what either partner is usually "
    "like, and a construct absent from this transcript may be common outside it.",
    "No dispositional traits. Attachment style, differentiation of self and personality are "
    "measured with validated instruments across contexts, never inferred from a transcript.",
    "No context: what preceded this exchange, what the couple's history is, what either "
    "partner meant or felt, and what happened afterwards are all outside the text.",
    "Only one side of the meaning. Each partner's account of what they intended is absent, "
    "and the coding is of words, not intentions.",
    "Cultural and linguistic norms for directness, volume and conflict expression vary "
    "widely, and the research these constructs come from drew mainly on white, "
    "middle-class, heterosexual US samples.",
]


class Analysis:
    def __init__(
        self,
        transcript: Transcript,
        language: str,
        language_confidence: float,
        safety: SafetyResult,
        results: list[ModuleResult],
    ) -> None:
        self.transcript = transcript
        self.language = language
        self.language_confidence = language_confidence
        self.safety = safety
        self.results = results
        self.timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    # ------------------------------------------------------------------ views
    @property
    def findings(self) -> list[Indicator]:
        out = [i for r in self.results for i in r.indicators if i.is_finding]
        return sorted(out, key=lambda i: (-i.confidence, i.indicator_id))

    @property
    def insufficient(self) -> list[Indicator]:
        return [i for r in self.results for i in r.indicators if not i.is_finding]

    @property
    def ruled_out(self) -> list:
        return [x for r in self.results for x in r.ruled_out]

    @property
    def not_assessable(self) -> list:
        return [x for r in self.results for x in r.not_assessable]

    @property
    def cycle(self) -> dict[str, Any] | None:
        for r in self.results:
            if r.cycle:
                return r.cycle
        return None

    @property
    def competing_readings(self) -> list[dict[str, Any]]:
        readings = [c for r in self.results for c in r.competing_readings]
        for ind in self.findings:
            if ind.confidence_band == "tentative" and ind.competing_reading:
                readings.append(
                    {
                        "reading": ind.competing_reading,
                        "applies_to": [ind.indicator_id],
                        "discriminating_data": (
                            "The recording or the partners' own account of this moment: tone "
                            "and timing would settle whether the span carries the coded "
                            "meaning, and more of the conversation would show whether it "
                            "repeats."
                        ),
                    }
                )
        if not readings:
            readings.append(
                {
                    "reading": (
                        "The exchange may be a single bad conversation rather than an "
                        "instance of any recurring pattern: everything coded here is "
                        "consistent with a one-off argument on an unusually hard day."
                    ),
                    "applies_to": [],
                    "discriminating_data": (
                        "Several conversations sampled across different days and topics; a "
                        "one-off would not reproduce the same sequence."
                    ),
                }
            )
        return readings

    @property
    def open_questions(self) -> list[str]:
        seen, out = set(), []
        for r in self.results:
            for q in r.open_questions:
                if q not in seen:
                    seen.add(q)
                    out.append(q)
        return out

    @property
    def limitations(self) -> list[str]:
        lim = list(STANDING_LIMITATIONS)
        if self.transcript.attribution_uncertain_turns:
            n = len(self.transcript.attribution_uncertain_turns)
            lim.insert(
                0,
                f"Speaker attribution is uncertain for {n} of "
                f"{len(self.transcript.turns)} turns. Misattributed turns invert the coding: "
                "a complaint credited to the wrong partner reverses the pattern described "
                "below. Confidence on affected indicators has been reduced, but the safest "
                "reading is that those codes are provisional.",
            )
        lim.extend(self.transcript.notes)
        if not self.safety.tripped:
            lim.append(
                "The safety screen found no markers of threat, violence, intimidation or "
                "coercive control. That is not a finding that none exist: one conversation "
                "is a sample, and such behavior is frequently not discussed on the record.",
            )
        return lim

    # ------------------------------------------------------------------- output
    def to_json(self) -> dict[str, Any]:
        tr = self.transcript
        counts: dict[str, int] = {}
        for t in tr.turns:
            counts[t.speaker] = counts.get(t.speaker, 0) + 1
        reverse = {v: k for k, v in tr.speaker_map.items()}
        doc: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "run": {
                "tool_version": __version__,
                "timestamp": self.timestamp,
                "input_format": tr.input_format,
                "language": self.language,
                "language_confidence": self.language_confidence,
                "anonymized": tr.anonymized,
                "modules_run": (
                    ["90-safety"]
                    if self.safety.halted_analysis
                    else ["90-safety"] + [r.module for r in self.results]
                ),
            },
            "transcript": {
                "turn_count": len(tr.turns),
                "speakers": [
                    {
                        "id": s,
                        "original_label": None if tr.anonymized else reverse.get(s),
                        "turn_count": counts.get(s, 0),
                    }
                    for s in tr.speakers
                ],
                "attribution_uncertain_turns": tr.attribution_uncertain_turns,
                "notes": tr.notes,
            },
            "safety_gate": self.safety.to_json(),
            "indicators": [],
            "insufficient_evidence": [],
            "ruled_out": [],
            "not_assessable": [],
            "cycle": None,
            "competing_readings": [],
            "open_questions": [],
            "limitations": self.limitations,
        }

        if self.safety.halted_analysis:
            # The analysis is withheld, not qualified: no cycle, no rule-outs, no readings
            # that would normalize the markers (90-safety.md sec. 3).
            doc["competing_readings"] = [
                {
                    "reading": (
                        "The safety markers may be hyperbole, reported speech, or a "
                        "misreading by this screen, which is a conservative heuristic with "
                        "no validation behind it for text."
                    ),
                    "discriminating_data": (
                        "Only the people involved, or a qualified professional speaking with "
                        "them separately and safely, can establish what these turns describe."
                    ),
                }
            ]
            doc["open_questions"] = [
                "Does either partner feel unsafe, or change their behavior to avoid the "
                "other's reaction?",
                "Is there a safe way for each partner to speak with someone separately?",
            ]
            return doc

        doc["indicators"] = [i.to_json() for i in self.findings]
        doc["insufficient_evidence"] = [
            {
                "module": i.module,
                "construct": i.construct,
                "confidence": i.confidence,
                "what_was_seen": i.rationale,
                "what_is_missing": i.what_is_missing
                or (
                    "The signal is below the evidentiary floor: too sparse or too ambiguous "
                    "to report as a finding."
                ),
                "evidence": [e.to_json() for e in i.evidence],
            }
            for i in self.insufficient
        ]
        doc["ruled_out"] = [x.to_json() for x in self.ruled_out]
        doc["not_assessable"] = [x.to_json() for x in self.not_assessable]
        doc["cycle"] = self.cycle
        doc["competing_readings"] = self.competing_readings
        doc["open_questions"] = self.open_questions
        return doc


def analyze(
    raw: str,
    *,
    input_format: str | None = None,
    anonymize: bool = True,
    language: str | None = None,
    request_text: str = "",
) -> Analysis | str:
    """Run the instrument. Returns an :class:`Analysis`, or a refusal string.

    The safety gate and the adversarial-use screen both run before any coding.
    """
    tr = normalize(raw, input_format=input_format, anonymize=anonymize)
    detected, conf = lang_mod.detect(raw)
    lg = language or detected

    refusal = screen_request(request_text, lg) or screen_request(request_text, "en")
    if refusal:
        return refusal

    safety = screen(tr, lg)
    if safety.halted_analysis:
        return Analysis(tr, lg, conf, safety, [])

    # Each module gets the transcript and the language. Nothing else, and nothing back.
    results = [fn(tr, lg) for _, fn in MODULES]
    return Analysis(tr, lg, conf, safety, results)


def validate(doc: dict[str, Any]) -> list[str]:
    """Contract checks that the JSON schema cannot express."""
    problems: list[str] = []
    gate = doc["safety_gate"]["halted_analysis"]

    if not gate and doc["indicators"] and not doc["ruled_out"]:
        problems.append(
            "ruled_out is empty while indicators were coded: an instrument that reports what "
            "it finds must also report what it looked for and did not find "
            "(00-epistemics.md sec. 6)."
        )
    if not gate and not doc["indicators"] and not doc["not_assessable"]:
        problems.append(
            "nothing was coded and nothing was declared unassessable: the run reported no "
            "state at all."
        )
    if not gate and not doc["competing_readings"]:
        problems.append("competing_readings is empty (00-epistemics.md sec. 7).")
    for ind in doc["indicators"]:
        if not ind["evidence"]:
            problems.append(f"{ind['indicator_id']}: finding with no quoted span.")
        if ind["confidence"] < EVIDENCE_FLOOR:
            problems.append(f"{ind['indicator_id']}: below the evidentiary floor but reported.")
        if ind["inference_level"] == "inferred" and ind["confidence"] > 0.65:
            problems.append(f"{ind['indicator_id']}: inferred indicator above the 0.65 cap.")
        if ind["unit"] == "dyad" and ind["speaker"] is not None:
            problems.append(f"{ind['indicator_id']}: dyad-level indicator carries a speaker.")
        for e in ind["evidence"]:
            if not e["quote"].strip():
                problems.append(f"{ind['indicator_id']}: empty quote.")
    if gate and (doc["indicators"] or doc["ruled_out"] or doc["cycle"]):
        problems.append(
            "The safety gate tripped but pattern analysis was emitted (90-safety.md sec. 3)."
        )
    return problems
