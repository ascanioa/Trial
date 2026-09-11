"""10 - Attachment: proximity-seeking and safe-haven functions in adult pairs.

Codes behavioral STRATEGIES visible in this exchange. Never assigns an attachment style to
a person: styles are dispositional and measured with validated instruments across contexts,
not inferred from one conversation. See reference/10-attachment.md.
"""

from __future__ import annotations

from .. import lexicon as L
from ..indicators import Indicator, ModuleResult, NotAssessable, RuledOut
from ..normalize import Transcript
from .base import dedupe, emit_per_speaker, matches, scan

MODULE = "10-attachment"
SRC_BOWLBY = "Bowlby (1969/1982, 1973); Ainsworth et al. (1978)"
SRC_HS = "Hazan & Shaver (1987)"
SRC_MS = "Mikulincer & Shaver (2016)"

NO_STYLE = (
    "Describes a move in this exchange, not a person. This does NOT indicate an attachment "
    "style: styles are dispositional, measured with validated instruments across contexts, "
    "and cannot be read from one conversation."
)


def code(tr: Transcript, lang: str) -> ModuleResult:
    res = ModuleResult(module=MODULE)
    dyad = tr.dyad
    if not dyad:
        return res

    emit_per_speaker(
        res, tr, lang, dyad, L.PROXIMITY_SEEKING,
        module=MODULE, indicator_id="attachment.proximity_seeking",
        construct="Proximity-seeking / safe-haven bid", theory_source=SRC_BOWLBY,
        rationale="A turn seeking contact, reassurance, or the partner's presence.",
        not_licensed=NO_STYLE,
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.SECURE_BASE,
        module=MODULE, indicator_id="attachment.safe_haven_response",
        construct="Safe-haven / secure-base response", theory_source=SRC_BOWLBY,
        rationale="A turn offering availability: presence, patience, or an offer to help.",
        not_licensed=NO_STYLE,
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.PROTEST,
        module=MODULE, indicator_id="attachment.protest",
        construct="Protest behavior", theory_source=SRC_BOWLBY,
        rationale=(
            "Escalated signaling aimed at re-establishing the partner's responsiveness, "
            "after a bid did not land."
        ),
        not_licensed=(
            NO_STYLE + " Bowlby's despair and detachment phases are longitudinal and are "
            "not coded at all."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.HYPERACTIVATING,
        module=MODULE, indicator_id="attachment.hyperactivating",
        construct="Hyperactivating move", theory_source=SRC_MS,
        rationale=(
            "Escalating the bid to force a response: testing, repeated demand, or an "
            "ultimatum used as a probe for reassurance."
        ),
        not_licensed=NO_STYLE,
        competing_reading=(
            "A single direct request is not hyperactivation. If the transcript does not show "
            "the earlier bid that went unanswered, this may be a first ask rather than an "
            "escalation."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.DEACTIVATING,
        module=MODULE, indicator_id="attachment.deactivating",
        construct="Deactivating move", theory_source=SRC_MS,
        rationale=(
            "Down-regulating the attachment signal: minimizing the issue, shifting away from "
            "the bond, or declining the exchange."
        ),
        not_licensed=NO_STYLE,
        competing_reading=(
            "Minimizing can be a genuine disagreement about how big the issue is, or a "
            "request for a break, rather than a move away from connection."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.SELF_RELIANCE_CLAIM,
        module=MODULE, indicator_id="attachment.self_reliance_claim",
        construct="Self-reliance claim", theory_source=SRC_MS,
        rationale="An explicit claim of not needing the partner, or of always having managed alone.",
        not_licensed=NO_STYLE,
    )

    found = {i.indicator_id for i in res.indicators if i.evidence}
    bids = [i for i in res.indicators if i.indicator_id == "attachment.proximity_seeking"]

    # Ruled out: the bid gives the response its occasion.
    if bids and "attachment.safe_haven_response" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Safe-haven response",
                basis=(
                    "Bids for contact are made, but no turn responds with availability — no "
                    "offer of presence, patience, or help. The construct had its occasion."
                ),
                counter_evidence=dedupe([e for i in bids for e in i.evidence])[:2],
            )
        )
    if bids and "attachment.protest" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Protest behavior",
                basis=(
                    "Bids for contact are made without escalation: no demand for an immediate "
                    "answer, no testing, no reproach for non-response."
                ),
                counter_evidence=dedupe([e for i in bids for e in i.evidence])[:2],
            )
        )
    deact = [i for i in res.indicators if i.indicator_id == "attachment.deactivating" and i.evidence]
    if deact and "attachment.hyperactivating" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Hyperactivating strategy",
                basis=(
                    "Moves away from the exchange occur without any matching escalation from "
                    "the other side: no repeated demand, no testing of the bond."
                ),
                counter_evidence=dedupe([e for i in deact for e in i.evidence])[:2],
            )
        )
    if not found:
        res.not_assessable.append(
            NotAssessable(
                module=MODULE,
                construct="Attachment strategies",
                reason=(
                    "Nothing in this transcript activates the attachment system — no bid for "
                    "contact, no separation, no distress directed at the partner. Attachment "
                    "strategies are visible under threat to the bond, and this exchange does "
                    "not supply that occasion."
                ),
            )
        )

    res.not_assessable.extend([
        NotAssessable(
            module=MODULE,
            construct="Attachment style / category for either partner",
            reason=(
                "Not assessable in principle from a transcript, and deliberately not "
                "attempted. Adult attachment is measured with validated instruments (the AAI, "
                "or self-report dimensional scales) administered outside the interaction. The "
                "two traditions converge only weakly with each other (Roisman et al., 2007), "
                "so a lexical reading of one conversation has no claim on the construct."
            ),
            measurement_layer="unmeasured",
        ),
        NotAssessable(
            module=MODULE,
            construct="Developmental / caregiving history",
            reason=(
                "Nothing about either partner's childhood or early caregiving is present in "
                "or inferable from a couple's conversation."
            ),
            measurement_layer="unmeasured",
        ),
        NotAssessable(
            module=MODULE,
            construct="Secure-base support for exploration",
            reason=(
                "Defined but deliberately not implemented. The markers that would signal it "
                "('take your time', 'go ahead') are not distinguishable in text from "
                "safe-haven comfort, and what separates them — whether the partner is "
                "exploring or distressed — lives in the situation rather than the wording. "
                "A detector would mostly re-code safe-haven responses under a second name."
            ),
            measurement_layer="unmeasured",
        ),
    ])
    res.open_questions.extend([
        "What did each partner do just before this exchange to try to reach the other?",
        "When one partner moved away here, what were they expecting would happen if they stayed?",
    ])
    return res
