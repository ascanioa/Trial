"""20 - Gottman & Levenson: observational conflict coding.

Operational definitions live in reference/20-gottman-levenson.md. This module implements
them over text only; the physiological layer of the original paradigm is reported as
unmeasured on every run.
"""

from __future__ import annotations

import re

from .. import lexicon as L
from ..indicators import Evidence, Indicator, ModuleResult, NotAssessable, RuledOut
from ..normalize import Transcript, Turn
from .base import by_speaker, emit, matches, scan, turn_hits

MODULE = "20-gottman-levenson"
SRC_HORSEMEN = "Gottman (1999); Gottman & Levenson (1992)"
SRC_STARTUP = "Gottman, Coan, Carrere & Swanson (1998)"
SRC_BIDS = "Driver & Gottman (2004)"
SRC_RATIO = "Gottman (1993)"
SRC_FLOOD = "Levenson & Gottman (1983, 1985); Gottman (1993)"

_STOP = {
    "the", "and", "you", "your", "that", "this", "with", "have", "just", "about", "what",
    "when", "were", "was", "for", "not", "but", "are", "did", "dont", "don't", "like",
    "para", "porque", "cuando", "pero", "que", "los", "las", "una", "con", "por", "del",
    "mas", "muy", "esta", "este", "eso", "esto", "como", "hay", "ser", "estar", "todo",
}


def _content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{4,}", L.fold(text)) if w not in _STOP}


def _minimal_lines(turn: Turn, lang: str) -> int:
    """How many of a turn's messages are minimal responses, or 0 if any is substantive.

    Consecutive same-speaker messages are merged into one turn by the normalizer, so a chat
    turn reading "Whatever." / "Fine." is two minimal responses, not one.
    """
    lines = [ln.strip() for ln in turn.text.splitlines() if ln.strip()] or [turn.text]
    for ln in lines:
        probe = Turn(index=turn.index, speaker=turn.speaker, text=ln)
        closed = matches(probe, L.STONEWALL_MINIMAL, lang)
        contentless = (
            len(ln.split()) <= 3 and "?" not in ln and not _content_words(ln)
        )
        if not (closed or contentless):
            return 0
    return len(lines)


def _is_minimal(turn: Turn, lang: str) -> bool:
    return _minimal_lines(turn, lang) > 0


def _timeout_legs(turn: Turn, lang: str) -> tuple[bool, bool, bool]:
    """(names state/need, proposes return, carries a parting shot) - 20-gottman sec. 1.2."""
    state = matches(turn, L.TIMEOUT_NEEDS_STATE, lang) or matches(
        turn, L.FLOODING_SELF_REPORT, lang
    )
    ret = matches(turn, L.TIMEOUT_RETURN, lang)
    shot = (
        matches(turn, L.PARTING_SHOT, lang)
        or matches(turn, L.CONTEMPT, lang)
        or matches(turn, L.GLOBAL_QUANTIFIER, lang)
    )
    return state, ret, shot


def _withdrawal_evidence(turn: Turn, lang: str) -> list[Evidence]:
    """One span per minimal message, so merged chat messages are not undercounted."""
    lines = [ln.strip() for ln in turn.text.splitlines() if ln.strip()]
    if len(lines) > 1 and _minimal_lines(turn, lang) >= 2:
        return [Evidence.from_turn(turn, ln) for ln in lines]
    return [Evidence.from_turn(turn, turn.text)]


def code(tr: Transcript, lang: str) -> ModuleResult:
    res = ModuleResult(module=MODULE)
    n_turns = len(tr.turns)
    dyad = tr.dyad
    turns = [t for t in tr.turns if t.speaker in dyad]
    if not turns:
        return res

    # ---------------------------------------------------------------- Four Horsemen
    global_hits = scan(tr, L.GLOBAL_QUANTIFIER, lang, speakers=dyad)
    trait_hits = scan(tr, L.TRAIT_ATTRIBUTION, lang, speakers=dyad)
    complaint_hits = scan(tr, L.SPECIFIC_COMPLAINT, lang, speakers=dyad)
    criticism_turns = {e.turn for e in global_hits} | {e.turn for e in trait_hits}

    for spk, evs in by_speaker(global_hits + trait_hits).items():
        emit(
            res,
            Indicator(
                indicator_id="gottman.criticism",
                module=MODULE,
                construct="Criticism",
                theory_source=SRC_HORSEMEN,
                unit="speaker",
                speaker=spk,
                evidence=_dedupe(evs),
                rationale=(
                    "The complaint is framed as a global or trait-level attribution about "
                    "the partner rather than as a specific behavior in a specific situation."
                ),
                not_licensed=(
                    "Does not make this speaker 'a critical person', and does not generalize "
                    "beyond the turns quoted."
                ),
            ),
            transcript_turns=n_turns,
        )

    # Specific complaints are coded in their own right: they are the near-miss that must not
    # be read as criticism, and they are the counter-evidence when criticism is ruled out.
    # A complaint raised to ward off a complaint is a counter-complaint, which this framework
    # codes as defensiveness; it is not additionally a complaint of its own.
    counter_complaint_turns = {
        t.index for t in turns if matches(t, L.DEFENSIVENESS, lang)
    }
    for spk, evs in by_speaker(
        [
            e for e in complaint_hits
            if e.turn not in criticism_turns and e.turn not in counter_complaint_turns
        ]
    ).items():
        emit(
            res,
            Indicator(
                indicator_id="gottman.complaint",
                module=MODULE,
                construct="Complaint (not criticism)",
                theory_source=SRC_HORSEMEN,
                unit="speaker",
                speaker=spk,
                evidence=_dedupe(evs),
                rationale=(
                    "A specific behavior in a specific situation, without global quantifiers "
                    "or character attribution. Gottman's frame treats this as distinct from "
                    "criticism, not as a milder form of it."
                ),
                not_licensed="Not a horseman. Carries no implication about the relationship.",
            ),
            transcript_turns=n_turns,
        )

    for spk, evs in by_speaker(scan(tr, L.CONTEMPT, lang, speakers=dyad)).items():
        emit(
            res,
            Indicator(
                indicator_id="gottman.contempt",
                module=MODULE,
                construct="Contempt",
                theory_source=SRC_HORSEMEN,
                unit="speaker",
                speaker=spk,
                evidence=_dedupe(evs),
                rationale=(
                    "Communication from a position of superiority: mockery, insult, or "
                    "derision, as distinct from anger expressed without that position."
                ),
                not_licensed=(
                    "Does not establish the speaker's intent, feelings toward the partner, "
                    "or a stable pattern outside this exchange."
                ),
            ),
            transcript_turns=n_turns,
        )

    # Defensiveness requires warding off WITHOUT taking responsibility; a turn that also
    # takes responsibility fails the definition and is dropped, not merely down-weighted.
    resp_turns = {
        t.index for t in turns if matches(t, L.ACCEPT_RESPONSIBILITY, lang)
    }
    def_hits = [
        e for e in scan(tr, L.DEFENSIVENESS, lang, speakers=dyad) if e.turn not in resp_turns
    ]
    for spk, evs in by_speaker(def_hits).items():
        emit(
            res,
            Indicator(
                indicator_id="gottman.defensiveness",
                module=MODULE,
                construct="Defensiveness",
                theory_source=SRC_HORSEMEN,
                unit="speaker",
                speaker=spk,
                evidence=_dedupe(evs),
                rationale=(
                    "Warding off a perceived attack — counter-complaint, innocent-victim "
                    "stance, or yes-but — with no responsibility taken in the same turn."
                ),
                not_licensed=(
                    "Does not establish that the complaint being warded off was accurate, "
                    "or that the speaker was in fact under attack."
                ),
            ),
            transcript_turns=n_turns,
        )

    # ------------------------------------------- Stonewalling vs. requested time-out
    timeouts: list[Evidence] = []
    stonewall_candidates: dict[str, list[tuple[Turn, bool]]] = {}  # speaker -> (turn, explicit)
    ambiguous_withdrawal: dict[str, str] = {}

    for t in turns:
        explicit = matches(t, L.STONEWALL_EXPLICIT, lang)
        minimal = _is_minimal(t, lang)
        state, ret, shot = _timeout_legs(t, lang)
        if state and ret and not shot:
            timeouts.append(Evidence.from_turn(t, t.text))
            continue  # a well-formed break is not stonewalling
        if not (explicit or minimal):
            continue
        if minimal and not explicit and (
            matches(t, L.REPAIR_UPTAKE, lang)
            or matches(t, L.POSITIVE_AFFECT, lang)
            or matches(t, L.ACCEPTING_INFLUENCE, lang)
        ):
            continue  # "Me too." / "Thank you." is brief agreement, not listener withdrawal
        if state and not ret:
            ambiguous_withdrawal[t.speaker] = (
                "The withdrawal names an internal state but proposes no return, so it sits "
                "between a stonewall and a break request that was never completed."
            )
        stonewall_candidates.setdefault(t.speaker, []).append((t, explicit))

    for spk, cands in stonewall_candidates.items():
        own = [t.index for t in tr.turns_of(spk)]
        minimal_idx = [t.index for t, exp in cands if not exp]
        explicit_any = any(exp for _, exp in cands)
        # Repetition test: two of the speaker's OWN consecutive turns are minimal, or one
        # turn holds two or more consecutive minimal messages.
        consecutive = any(
            own.index(a) + 1 < len(own) and own[own.index(a) + 1] in minimal_idx
            for a in minimal_idx
            if a in own
        ) or any(_minimal_lines(t, lang) >= 2 for t, exp in cands if not exp)
        if not (explicit_any or consecutive):
            # A single minimal turn is a data point, not a pattern (00-epistemics sec. 3.1).
            t0 = cands[0][0]
            res.indicators.append(
                Indicator(
                    indicator_id="gottman.stonewalling",
                    module=MODULE,
                    construct="Stonewalling",
                    theory_source=SRC_HORSEMEN,
                    unit="speaker",
                    speaker=spk,
                    evidence=_withdrawal_evidence(t0, lang),
                    rationale="A single minimal response, with no repetition and no explicit refusal to engage.",
                    not_licensed="Not codeable as stonewalling on one turn.",
                    what_is_missing=(
                        "Listener withdrawal is a sustained state: it needs repetition across "
                        "the speaker's consecutive turns, or an explicit refusal to engage. "
                        "Neither is present."
                    ),
                    confidence=0.3,
                    confidence_band="insufficient",
                    confidence_factors=["single minimal turn; repetition criterion not met"],
                )
            )
            continue
        ind = Indicator(
            indicator_id="gottman.stonewalling",
            module=MODULE,
            construct="Stonewalling",
            theory_source=SRC_HORSEMEN,
            unit="speaker",
            speaker=spk,
            evidence=[e for t, _ in cands for e in _withdrawal_evidence(t, lang)],
            rationale=(
                "Listener withdrawal from the interaction: "
                + ("an explicit refusal to engage" if explicit_any else "")
                + (" and " if explicit_any and consecutive else "")
                + ("minimal responses across the speaker's consecutive turns" if consecutive else "")
                + ". The turns do not meet the time-out criteria (named need, proposed "
                "return, no parting shot)."
            ),
            not_licensed=(
                "Does not establish the speaker's internal state. Withdrawal in text cannot "
                "be distinguished from physiological overwhelm, which is unmeasured here."
            ),
            ambiguous=spk in ambiguous_withdrawal,
            competing_reading=ambiguous_withdrawal.get(spk),
        )
        emit(res, ind, transcript_turns=n_turns)

    if timeouts:
        for spk, evs in by_speaker(timeouts).items():
            emit(
                res,
                Indicator(
                    indicator_id="gottman.time_out_request",
                    module=MODULE,
                    construct="Requested time-out (not stonewalling)",
                    theory_source=SRC_HORSEMEN,
                    unit="speaker",
                    speaker=spk,
                    evidence=evs,
                    rationale=(
                        "The withdrawal names the speaker's state or need, proposes a return, "
                        "and carries no parting shot. Taking a break when overwhelmed is the "
                        "behavior this framework recommends, not the one it codes as a horseman."
                    ),
                    not_licensed="Says nothing about whether the break was honored afterwards.",
                ),
                transcript_turns=n_turns,
            )

    # ----------------------------------------------------------------------- Startup
    substantive = [t for t in turns if len(t.text.split()) >= 5]
    if substantive:
        first = substantive[0]
        harsh = (
            turn_hits(first, L.GLOBAL_QUANTIFIER, lang)
            + turn_hits(first, L.TRAIT_ATTRIBUTION, lang)
            + turn_hits(first, L.CONTEMPT, lang)
        )
        soft = (
            []
            if matches(first, L.CHANGE_DEMAND, lang)
            else turn_hits(first, L.I_STATEMENT, lang)
        )
        if harsh:
            emit(
                res,
                Indicator(
                    indicator_id="gottman.harsh_startup",
                    module=MODULE,
                    construct="Harsh startup",
                    theory_source=SRC_STARTUP,
                    unit="speaker",
                    speaker=first.speaker,
                    evidence=_dedupe(harsh),
                    rationale=(
                        f"The first substantive turn (turn {first.index}) opens with "
                        "criticism, contempt, or an accusatory frame."
                    ),
                    not_licensed=(
                        "Turn position is a coarse proxy for the original time-window "
                        "measure, and predicts nothing about this conversation's outcome."
                    ),
                ),
                transcript_turns=n_turns,
            )
        elif soft:
            emit(
                res,
                Indicator(
                    indicator_id="gottman.softened_startup",
                    module=MODULE,
                    construct="Softened startup",
                    theory_source=SRC_STARTUP,
                    unit="speaker",
                    speaker=first.speaker,
                    evidence=_dedupe(soft),
                    rationale=(
                        f"The first substantive turn (turn {first.index}) uses an "
                        "I-statement about a situation, without character attribution."
                    ),
                    not_licensed="Says nothing about how the rest of the conversation went.",
                ),
                transcript_turns=n_turns,
            )

    # ------------------------------------------------------- Bids and turning toward
    for t in turns:
        bid_hits = turn_hits(t, L.BID, lang)
        if not bid_hits:
            continue
        nxt = tr.next_turn(t.index)
        if nxt is None:
            res.not_assessable.append(
                NotAssessable(
                    module=MODULE,
                    construct="Response to bid (turn %d)" % t.index,
                    reason="The bid is the final turn; the transcript ends before any response.",
                )
            )
            continue
        if nxt.speaker == t.speaker:
            continue
        against = turn_hits(nxt, L.TURNING_AGAINST, lang) + turn_hits(nxt, L.CONTEMPT, lang)
        overlap = _content_words(t.text) & _content_words(nxt.text)
        engaged = (
            bool(overlap)
            or matches(nxt, L.REPAIR_UPTAKE, lang)
            or matches(nxt, L.ACCEPTING_INFLUENCE, lang)
        )
        if against:
            kind, label, rationale, level = (
                "gottman.turning_against",
                "Turning against a bid",
                "The response to the bid carries irritation, dismissal, or hostility.",
                "observed",
            )
            ev = [Evidence.from_turn(t, t.text)] + _dedupe(against)
        elif engaged:
            kind, label, rationale, level = (
                "gottman.turning_toward",
                "Turning toward a bid",
                "The next turn takes up the content of the bid.",
                "inferred",
            )
            ev = [Evidence.from_turn(t, t.text), Evidence.from_turn(nxt, nxt.text)]
        elif (
            _is_minimal(nxt, lang)
            or matches(nxt, L.TOPIC_SHIFT, lang)
            or matches(nxt, L.DEACTIVATING, lang)
            or matches(nxt, L.OBLIGATION_DEFLECTION, lang)
        ):
            kind, label, rationale, level = (
                "gottman.turning_away",
                "Turning away from a bid",
                "The next turn does not take up the bid's content and moves elsewhere - a "
                "topic shift, an obligation cited instead, or a minimal reply.",
                "inferred",
            )
            ev = [Evidence.from_turn(t, t.text), Evidence.from_turn(nxt, nxt.text)]
        else:
            # No shared content and no disengagement marker: a response can engage a bid
            # without repeating its words, and text alone cannot settle which happened.
            res.not_assessable.append(
                NotAssessable(
                    module=MODULE,
                    construct=f"Uptake of bid (turns {t.index}-{nxt.index})",
                    reason=(
                        "The response shares no wording with the bid but shows no sign of "
                        "moving away from it either. Whether it engaged the bid is not "
                        "readable from the text."
                    ),
                )
            )
            continue
        emit(
            res,
            Indicator(
                indicator_id=kind,
                module=MODULE,
                construct=label,
                theory_source=SRC_BIDS,
                unit="dyad",
                evidence=ev,
                inference_level=level,
                rationale=rationale + f" Adjacency pair: turns {t.index} and {nxt.index}.",
                not_licensed=(
                    "Uptake is judged from lexical content only; a response can engage a bid "
                    "without repeating its words, and tone is not available in text."
                ),
                competing_reading=(
                    None
                    if level == "observed"
                    else "The response may engage the bid in a way this text-only test cannot see."
                ),
            ),
            transcript_turns=n_turns,
        )

    # ------------------------------------------------------------------ Repair
    repair_turns = [t for t in turns if matches(t, L.REPAIR, lang)]
    for spk, evs in by_speaker(
        [e for t in repair_turns for e in turn_hits(t, L.REPAIR, lang)]
    ).items():
        emit(
            res,
            Indicator(
                indicator_id="gottman.repair_attempt",
                module=MODULE,
                construct="Repair attempt",
                theory_source=SRC_HORSEMEN,
                unit="speaker",
                speaker=spk,
                evidence=_dedupe(evs),
                rationale="Moves to de-escalate or interrupt the negativity in progress.",
                not_licensed=(
                    "Presence of a repair attempt says nothing about sincerity, and nothing "
                    "about the relationship's trajectory."
                ),
            ),
            transcript_turns=n_turns,
        )

    landed: list[Evidence] = []
    missed: list[Evidence] = []
    missed_escalated = False
    for t in repair_turns:
        nxt = tr.next_turn(t.index)
        if nxt is None or nxt.speaker == t.speaker:
            res.not_assessable.append(
                NotAssessable(
                    module=MODULE,
                    construct=f"Reception of repair attempt (turn {t.index})",
                    reason="No partner turn follows the repair attempt in this transcript.",
                )
            )
            continue
        escalates = (
            matches(nxt, L.CONTEMPT, lang)
            or matches(nxt, L.GLOBAL_QUANTIFIER, lang)
            or matches(nxt, L.TRAIT_ATTRIBUTION, lang)
            or matches(nxt, L.DEFENSIVENESS, lang)
        )
        received = (
            matches(nxt, L.REPAIR_UPTAKE, lang)
            or matches(nxt, L.ACCEPTING_INFLUENCE, lang)
            or matches(nxt, L.REPAIR, lang)
        ) and not escalates
        pair = [Evidence.from_turn(t, t.text), Evidence.from_turn(nxt, nxt.text)]
        withdraws = _is_minimal(nxt, lang) or matches(nxt, L.STONEWALL_EXPLICIT, lang)
        if received:
            landed.extend(pair)
        elif escalates or withdraws:
            missed.extend(pair)
            missed_escalated = missed_escalated or escalates
        else:
            res.not_assessable.append(
                NotAssessable(
                    module=MODULE,
                    construct=f"Reception of repair attempt (turn {t.index})",
                    reason=(
                        f"Turn {nxt.index} neither takes up the repair nor continues the "
                        "negativity, so whether the repair landed cannot be read from the text."
                    ),
                )
            )

    if landed:
        emit(
            res,
            Indicator(
                indicator_id="gottman.repair_received",
                module=MODULE,
                construct="Repair received",
                theory_source=SRC_HORSEMEN,
                unit="dyad",
                evidence=landed,
                rationale=(
                    "The turn following the repair takes it up and de-escalates. Whether a "
                    "repair lands is a property of the pair, not of either partner."
                ),
                not_licensed=(
                    "Not a judgment of either partner, and not a sign the underlying issue "
                    "was resolved."
                ),
            ),
            transcript_turns=n_turns,
        )
    if missed:
        emit(
            res,
            Indicator(
                indicator_id="gottman.repair_not_received",
                module=MODULE,
                construct="Repair not received",
                theory_source=SRC_HORSEMEN,
                unit="dyad",
                evidence=missed,
                inference_level="observed",
                rationale=(
                    "The turn following the repair continues or escalates the negativity "
                    "rather than taking it up. Whether a repair lands is a property of the "
                    "pair, not of either partner."
                ),
                not_licensed=(
                    "Not a judgment of either partner. A repair can fail to land because it "
                    "was mistimed, unclear, or preceded by an injury the text does not show."
                ),
                competing_reading=(
                    None if missed_escalated
                    else "The partner withdrew rather than answering; withdrawal after a "
                    "repair can also mean the repair landed but came too late to answer."
                ),
            ),
            transcript_turns=n_turns,
        )

    # --------------------------------------------------------- Accepting influence
    infl = scan(tr, L.ACCEPTING_INFLUENCE, lang, speakers=dyad)
    for spk, evs in by_speaker(infl).items():
        emit(
            res,
            Indicator(
                indicator_id="gottman.accepting_influence",
                module=MODULE,
                construct="Accepting influence",
                theory_source=SRC_STARTUP,
                unit="speaker",
                speaker=spk,
                evidence=_dedupe(evs),
                rationale="The speaker yields to, or incorporates, the partner's position.",
                not_licensed=(
                    "The original finding concerned husbands in heterosexual newlywed "
                    "couples at the group level; it is not reproduced here as a gendered "
                    "claim and does not transfer to an individual couple."
                ),
            ),
            transcript_turns=n_turns,
        )
    accepting_speakers = {e.speaker for e in infl}
    for spk in dyad:
        if spk in accepting_speakers:
            continue
        refusals = [
            e for e in scan(tr, L.REFUSAL, lang, speakers=[spk])
            + scan(tr, L.DEFENSIVENESS, lang, speakers=[spk])
        ]
        yielded = any(
            matches(t, L.COMPLIANCE, lang)
            or matches(t, L.CONCRETE_AGREEMENT, lang)
            or matches(t, L.VAGUE_AGREEMENT, lang)
            for t in tr.turns_of(spk)
        )
        if len(refusals) >= 2 and not yielded:
            emit(
                res,
                Indicator(
                    indicator_id="gottman.rejecting_influence",
                    module=MODULE,
                    construct="Rejecting influence",
                    theory_source=SRC_STARTUP,
                    unit="speaker",
                    speaker=spk,
                    evidence=_dedupe(refusals)[:4],
                    inference_level="inferred",
                    rationale=(
                        "No turn by this speaker takes up any part of the partner's position, "
                        "while several counter or refuse it. The claim rests partly on an "
                        "absence across the transcript, not only on the quoted spans."
                    ),
                    not_licensed=(
                        "An absence in one conversation is weak evidence. A speaker may yield "
                        "in ways text does not record, or later in an exchange not sampled here."
                    ),
                    competing_reading=(
                        "The speaker may be holding a position they consider non-negotiable "
                        "on this one issue rather than refusing influence generally."
                    ),
                ),
                transcript_turns=n_turns,
            )

    # ---------------------------------------------------------- Self-reported flooding
    for spk, evs in by_speaker(scan(tr, L.FLOODING_SELF_REPORT, lang, speakers=dyad)).items():
        emit(
            res,
            Indicator(
                indicator_id="gottman.self_reported_flooding",
                module=MODULE,
                construct="Self-reported overwhelm (physiological layer unmeasured)",
                theory_source=SRC_FLOOD,
                unit="speaker",
                speaker=spk,
                evidence=_dedupe(evs),
                rationale=(
                    "The speaker states overwhelm or a need to stop. This is a self-report of "
                    "a subjective state."
                ),
                not_licensed=(
                    "This is NOT evidence of diffuse physiological arousal. Heart rate, skin "
                    "conductance, and physiological linkage between partners — the actual "
                    "constructs in Levenson's work — are not observable in text and are not "
                    "measured here."
                ),
            ),
            transcript_turns=n_turns,
        )

    # ------------------------------------------------------------ Positive:negative
    pos = scan(tr, L.POSITIVE_AFFECT, lang, speakers=dyad)
    neg = scan(tr, L.NEGATIVE_AFFECT, lang, speakers=dyad)
    if pos or neg:
        emit(
            res,
            Indicator(
                indicator_id="gottman.pos_neg_ratio",
                module=MODULE,
                construct="Positive-to-negative speech acts during conflict",
                theory_source=SRC_RATIO,
                unit="dyad",
                evidence=_dedupe(pos)[:3] + _dedupe(neg)[:3],
                rationale=(
                    f"{len(pos)} positively-valenced and {len(neg)} negatively-valenced "
                    f"speech acts were counted across {len(turns)} coded turns "
                    f"(ratio {len(pos)}:{len(neg)}). Reported as a raw count pair."
                ),
                not_licensed=(
                    "This must NOT be compared to the 5:1 figure. That ratio came from trained "
                    "coders using SPAFF on video with access to affect, tone and face, and was "
                    "derived at the level of group differences. A lexical count over text is a "
                    "different measurement with unknown correspondence to it, and applying a "
                    "group-level threshold to one conversation is a base-rate error."
                ),
            ),
            transcript_turns=n_turns,
        )

    # --------------------------------------------------- Ruled out / not assessable
    _rule_out(res, tr, lang, dyad, n_turns, timeouts)

    res.not_assessable.append(
        NotAssessable(
            module=MODULE,
            construct="Diffuse physiological arousal (flooding), physiological linkage",
            reason=(
                "Levenson's contribution to this paradigm is physiological — heart rate, skin "
                "conductance, and cross-partner linkage during conflict. None of it has a "
                "textual proxy. It is unmeasured here, not absent."
            ),
            measurement_layer="unmeasured",
        )
    )
    res.not_assessable.append(
        NotAssessable(
            module=MODULE,
            construct="Affect coding (SPAFF: tone, facial expression, prosody)",
            reason=(
                "The constructs were operationalized for video coding. Sarcasm, warmth and "
                "contempt are carried substantially by tone and face, which text does not have."
            ),
            measurement_layer="unmeasured",
        )
    )

    res.open_questions.extend(
        [
            "What happened in the minutes before this transcript begins? Startup coding "
            "depends on where the recording starts.",
            "Was the withdrawal in this conversation typical, or specific to this topic?",
            "What did each partner think the other was feeling at the sharpest moment?",
        ]
    )
    return res


def _rule_out(
    res: ModuleResult,
    tr: Transcript,
    lang: str,
    dyad: list[str],
    n_turns: int,
    timeouts: list[Evidence],
) -> None:
    """Actively searched, not found, where the transcript gave it an occasion."""
    findings = {i.indicator_id for i in res.indicators if i.is_finding}
    found = {i.indicator_id for i in res.indicators if i.evidence}
    conflict_present = bool(
        findings & {
            "gottman.criticism", "gottman.complaint", "gottman.defensiveness",
            "gottman.contempt", "gottman.stonewalling", "gottman.harsh_startup",
        }
    ) or len(scan(tr, L.NEGATIVE_AFFECT, lang, speakers=dyad)) >= 2 or bool(
        # An issue raised warmly is still an occasion: the exchange had somewhere to
        # escalate to and did not go there.
        findings & {"gottman.softened_startup", "gottman.repair_attempt"}
    )

    # Counter-evidence: registers the exchange stayed in, having had the occasion to escalate.
    counter_pool = (
        scan(tr, L.SPECIFIC_COMPLAINT, lang, speakers=dyad)
        + scan(tr, L.I_STATEMENT, lang, speakers=dyad)
        + scan(tr, L.REPAIR, lang, speakers=dyad)
        + scan(tr, L.ACCEPT_RESPONSIBILITY, lang, speakers=dyad)
    )

    checks = [
        ("gottman.contempt", "Contempt",
         "No turn communicates from a position of superiority — no insult, mockery, "
         "name-calling or derision — although the exchange carried enough heat to give it "
         "an occasion."),
        ("gottman.criticism", "Criticism",
         "Complaints in this transcript stay tied to specific behavior in specific "
         "situations; no global quantifier or character attribution appears."),
        ("gottman.defensiveness", "Defensiveness",
         "Turns responding to complaints take some responsibility or engage the content "
         "rather than warding it off."),
        ("gottman.stonewalling", "Stonewalling",
         "No sustained listener withdrawal: no explicit refusal to engage, and no repetition "
         "of minimal responses across a speaker's consecutive turns."),
        ("gottman.repair_attempt", "Repair attempts",
         "No turn attempts to de-escalate, apologize, soften, or interrupt the negativity."),
    ]
    for ind_id, name, basis in checks:
        if ind_id in found:
            continue
        # Withdrawal that met the time-out criteria is its own occasion: the construct had
        # every chance to appear and was actively discriminated away from.
        if ind_id == "gottman.stonewalling" and timeouts:
            res.ruled_out.append(
                RuledOut(
                    module=MODULE,
                    construct=name,
                    basis=(
                        "Withdrawal does occur, but it meets the time-out criteria — the "
                        "speaker names their state, proposes a return, and adds no parting "
                        "shot — which is the discrimination this module is required to make."
                    ),
                    counter_evidence=timeouts[:2],
                )
            )
            continue
        if not conflict_present:
            res.not_assessable.append(
                NotAssessable(
                    module=MODULE,
                    construct=name,
                    reason=(
                        "This transcript contains no conflict sequence, so the construct had "
                        "no occasion to appear. Absence here is absence of opportunity."
                    ),
                )
            )
            continue
        counter = counter_pool[:2]
        res.ruled_out.append(
            RuledOut(module=MODULE, construct=name, basis=basis, counter_evidence=counter)
        )


def _dedupe(evs: list[Evidence]) -> list[Evidence]:
    seen: set[tuple[int, str]] = set()
    out: list[Evidence] = []
    for e in evs:
        key = (e.turn, e.quote)
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out
