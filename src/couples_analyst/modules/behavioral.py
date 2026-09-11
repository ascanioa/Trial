"""60 - Behavioral couple therapy: Jacobson, Gurman, IBCT.

The most directly observable module here; its risk is the opposite of the others - treating
surface behavior as the whole story, which is the critique Gurman has pressed against
behavioral couple therapy. See reference/60-behavioral.md.
"""

from __future__ import annotations

from .. import lexicon as L
from ..indicators import Evidence, Indicator, ModuleResult, NotAssessable, RuledOut
from ..normalize import Transcript
from .base import dedupe, emit, emit_per_speaker, matches, scan, turn_hits

MODULE = "60-behavioral"
SRC_JM = "Jacobson & Margolin (1979)"
SRC_PATTERSON = "Patterson (1982)"
SRC_IBCT = "Jacobson & Christensen (1996)"


def code(tr: Transcript, lang: str) -> ModuleResult:
    res = ModuleResult(module=MODULE)
    dyad = tr.dyad
    if not dyad:
        return res
    n_turns = len(tr.turns)

    emit_per_speaker(
        res, tr, lang, dyad, L.REQUEST,
        module=MODULE, indicator_id="behavioral.request",
        construct="Request", theory_source=SRC_JM,
        rationale="A direct request for the partner to do something.",
        not_licensed="Coded symmetrically. Requests are not evidence of who is more reasonable.",
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.REFUSAL,
        module=MODULE, indicator_id="behavioral.refusal",
        construct="Refusal", theory_source=SRC_JM,
        rationale="A refusal of a request or proposal.",
        not_licensed="Coded symmetrically. A refusal is not a fault; the instrument takes no view on whether the request should have been granted.",
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.CONCRETE_AGREEMENT,
        module=MODULE, indicator_id="behavioral.concrete_agreement",
        construct="Concrete agreement", theory_source=SRC_JM,
        rationale="An agreement specifying a behavior together with a time, frequency, or trigger.",
        not_licensed=(
            "Says nothing about whether the agreement will be kept. Concreteness is about "
            "specifiability, not sincerity."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.VAGUE_AGREEMENT,
        module=MODULE, indicator_id="behavioral.vague_agreement",
        construct="Vague agreement", theory_source=SRC_JM,
        rationale="An agreement with no specified behavior, time, or trigger.",
        not_licensed=(
            "'I'll try' may be entirely sincere. The code concerns what the agreement "
            "specifies, not the speaker's intention or character."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.REINFORCEMENT_EROSION,
        module=MODULE, indicator_id="behavioral.reinforcement_erosion",
        construct="Reinforcement erosion (voiced)", theory_source=SRC_JM,
        rationale=(
            "A partner states that behavior which used to matter no longer registers, or "
            "that a positive act is now merely expected."
        ),
        not_licensed=(
            "Codes the statement. The process itself unfolds over months or years and is not "
            "observable in a transcript. Reinforcement language is an analogy here, not a "
            "demonstrated mechanism."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.COST_REWARD,
        module=MODULE, indicator_id="behavioral.exchange_asymmetry",
        construct="Behavior-exchange asymmetry claimed", theory_source=SRC_JM,
        rationale="Explicit scorekeeping about who does, gives, or concedes more.",
        not_licensed=(
            "Codes the claim, not its accuracy. This indicator may rest on the same span as "
            "50-interdependence's voiced costs and rewards: two frameworks reading one "
            "utterance, not two pieces of evidence."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.ACCEPTANCE_MOVE,
        module=MODULE, indicator_id="behavioral.acceptance_move",
        construct="Acceptance move (IBCT)", theory_source=SRC_IBCT,
        rationale="A turn that accepts a difference rather than contesting it.",
        not_licensed=(
            "Does not indicate that this couple needs acceptance work, or any therapy. IBCT "
            "holds couples need both acceptance and change; the balance is a clinical "
            "judgment made with the couple present."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.CHANGE_DEMAND,
        module=MODULE, indicator_id="behavioral.change_demand",
        construct="Change demand (IBCT)", theory_source=SRC_IBCT,
        rationale="A turn pressing for a change in the partner's behavior.",
        not_licensed="Not negative in itself. IBCT treats change as one of two necessary poles.",
    )

    # ------------------------------------------------------- coercion contingency
    pressure_turns = [t for t in tr.turns if t.speaker in dyad and matches(t, L.COERCIVE_PRESSURE, lang)]
    for spk in {t.speaker for t in pressure_turns}:
        evs = [e for t in pressure_turns if t.speaker == spk
               for e in turn_hits(t, L.COERCIVE_PRESSURE, lang)]
        emit(
            res,
            Indicator(
                indicator_id="behavioral.coercive_pressure",
                module=MODULE,
                construct="Aversive pressure sustained until compliance",
                theory_source=SRC_PATTERSON,
                unit="speaker",
                speaker=spk,
                evidence=dedupe(evs),
                rationale=(
                    "Pressure maintained or escalated past a refusal, which is the half of "
                    "the coercion contingency that is visible in text."
                ),
                not_licensed=(
                    "This is Patterson's learning process, present in ordinary distressed "
                    "couples. It is NOT coercive control in the sense of the safety gate, "
                    "which concerns domination through fear, surveillance and restriction of "
                    "liberty. The two must not be conflated."
                ),
            ),
            transcript_turns=n_turns,
        )

    # The contingency needs both halves in sequence: pressure, then the partner yielding.
    # Coded on the yielding partner, per 60-behavioral.md sec. 1.2.
    yields_by_speaker: dict[str, list[Evidence]] = {}
    for t in pressure_turns:
        nxt = tr.next_turn(t.index)
        if nxt is not None and nxt.speaker != t.speaker and matches(nxt, L.COMPLIANCE, lang):
            yields_by_speaker.setdefault(nxt.speaker, []).extend(
                [Evidence.from_turn(t, t.text), Evidence.from_turn(nxt, nxt.text)]
            )
    for spk, evs in yields_by_speaker.items():
        emit(
            res,
            Indicator(
                indicator_id="behavioral.compliance_under_pressure",
                module=MODULE,
                construct="Compliance under pressure",
                theory_source=SRC_PATTERSON,
                unit="speaker",
                speaker=spk,
                evidence=dedupe(evs),
                rationale=(
                    "This speaker yields immediately after sustained pressure from the "
                    "partner. Both halves of the contingency are present in sequence, which "
                    "is what distinguishes it from a single demand that happened to be met."
                ),
                not_licensed=(
                    "Not a judgment of the speaker, and not evidence of a trained pattern: "
                    "Patterson's cycle is a learning history built over many repetitions, "
                    "which one conversation cannot show. Yielding here is also not consent "
                    "to the pressure."
                ),
            ),
            transcript_turns=n_turns,
        )
    if not yields_by_speaker and pressure_turns:
        res.not_assessable.append(
            NotAssessable(
                module=MODULE,
                construct="Compliance under pressure (the contingency's second half)",
                reason=(
                    "Pressure occurs, but the transcript does not show the partner yielding "
                    "immediately after it. Without the second half, what reinforces what "
                    "cannot be read from the text."
                ),
            )
        )

    # ------------------------------------------------------------------ ruled out
    found = {i.indicator_id for i in res.indicators if i.evidence}
    requests = [i for i in res.indicators if i.indicator_id == "behavioral.request" and i.evidence]
    if requests and "behavioral.coercive_pressure" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Coercive pressure",
                basis=(
                    "Requests are made and not all are granted, but none is pursued with "
                    "escalating aversive pressure: no repetition past a refusal, no threat to "
                    "keep raising it, no conditional withholding."
                ),
                counter_evidence=dedupe([e for i in requests for e in i.evidence])[:2],
            )
        )
    if "behavioral.concrete_agreement" in found and "behavioral.vague_agreement" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Vague agreement",
                basis=(
                    "The agreements reached here specify a behavior and a time or trigger, "
                    "rather than resolving into 'I'll try' or 'we'll see'."
                ),
                counter_evidence=dedupe(scan(tr, L.CONCRETE_AGREEMENT, lang, speakers=dyad))[:2],
            )
        )
    if "behavioral.change_demand" in found and "behavioral.acceptance_move" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Acceptance move",
                basis=(
                    "Change is pressed for, but no turn accepts a difference as a difference: "
                    "nothing is framed as 'this is how you are and I can live with it'."
                ),
                counter_evidence=dedupe(scan(tr, L.CHANGE_DEMAND, lang, speakers=dyad))[:2],
            )
        )
    if requests and "behavioral.concrete_agreement" not in found and "behavioral.vague_agreement" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Agreement of any kind",
                basis=(
                    "Requests are made, but the exchange produces no agreement at all — "
                    "neither a concrete commitment nor a vague one."
                ),
                counter_evidence=dedupe([e for i in requests for e in i.evidence])[:2],
            )
        )
    if not found and not pressure_turns:
        res.not_assessable.append(
            NotAssessable(
                module=MODULE,
                construct="Behavioral exchange constructs",
                reason=(
                    "The exchange contains no requests, refusals, negotiations or agreements, "
                    "so there is no behavioral exchange to code."
                ),
            )
        )

    res.not_assessable.append(
        NotAssessable(
            module=MODULE,
            construct="Whether agreements are kept; rates of behavior at home",
            reason=(
                "Behavioral couple therapy assesses these with daily tracking outside the "
                "session. Frequency counts inside one conversation correspond imperfectly to "
                "what happens at home, and nothing here shows follow-through."
            ),
            measurement_layer="unmeasured",
        )
    )
    res.open_questions.extend([
        "What has each partner already tried about this, and what happened when they did?",
        "Which of the differences under discussion does each partner think is changeable?",
    ])
    return res
